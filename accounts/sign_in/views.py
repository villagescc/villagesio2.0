from django.urls import reverse, reverse_lazy
from django.views.generic.edit import FormView
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render as django_render
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.conf import settings

from django_user_agents.utils import get_user_agent

from accounts.forms import UserLoginForm
from profile.models import Profile
from general.mail import send_mail_from_system
from profile.models import Settings
from geo.models import Location
from profile.forms import PreRegistrationForm, RegistrationForm, ProfileForm

import mailchimp
import requests


# Session key to store invite code for later signing up.
INVITE_CODE_KEY = 'invite_code'

# Session key for profile ID of link sharer.
SHARED_BY_PROFILE_ID_KEY = 'shared_by'

# URL param key for username of link sharer.
SHARED_BY_USERNAME_KEY = 'u'

MESSAGES = {
    'profile_saved': _("Profile saved."),
    'contact_sent': _("Message sent."),
    'registration_done': _("Thank you for registering. "
                           "Please continue filling out your profile by "
                           "uploading a photo and describing yourself for other "
                           "users.<br><br>"
                           "We have sent a welcome email to your address. "
                           "If you do not receive it, please verify your email "
                           "address under account settings."),
    'password_changed': _("Password changed."),
    'settings_changed': _("Settings saved."),
    'email_updated': _("Settings saved. "
                       "A confirmation email has been sent to your new address. "
                       "If you do not receive it, please verify that you have "
                       "entered the correct email."),
    'invitation_sent': _("Invitation sent to %s."),
    'invitation_deleted': _("Invitation deleted."),
    'invitation_request_sent': _("Invitation request sent."),
    'invitation_landing': _("%s has invited you to Villages.io. "
                            "Please take a look around and then use the "
                            "<em>Join</em> link on the right to register."),
    'password_link_sent': _("A password reset link has been emailed to you."),
    'password_reset': _("Your password has been reset. You may now log in "
                        "with your new password."),
}


def subscribe_mailchimp(profile):

    postal_code = ''
    if profile.location:
        neighborhood = profile.location.neighborhood.replace(' ', '+').encode('UTF-8')
        city = profile.location.city.replace(' ', '+').encode('UTF-8')
        state = profile.location.state

        lon = profile.location.point.coords[0]
        lat = profile.location.point.coords[1]

        google_geo_endpoint_address = 'https://maps.googleapis.com/maps/api/geocode/json?address=1+{0},{1},{2}&key=AIzaSyBQAqenEQSDy5T5KNnyXBwOc-GmvSB8TQA'.format(
            neighborhood, city, state)
        google_geo_endpoint_coords = 'https://maps.googleapis.com/maps/api/geocode/json?latlng={0}, {1}&key=AIzaSyBQAqenEQSDy5T5KNnyXBwOc-GmvSB8TQA'.format(
            lat, lon)

        response = requests.get(google_geo_endpoint_address).json()

        if response["results"][0].get("address_components"):
            for each_type in response["results"][0]["address_components"]:
                for type in each_type['types']:
                    if type == 'postal_code':
                        postal_code = each_type.get('long_name').encode('UTF-8')
                        break

    API_KEY = settings.MAILCHIMP_APIKEY
    LIST_ID = '063533ab5b'

    try:
        api = mailchimp.Mailchimp(API_KEY)
        api.lists.subscribe(LIST_ID, {'name': profile.name,
                                      'email': profile.settings.email,
                                      'zipcode': postal_code if postal_code else ''},
                            send_welcome=False, double_optin=False)
    except Exception as e:
        print(e)

    return


class AuthView(FormView):
    template_name = 'new_templates/auth.html'

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())
        return super(AuthView, self).dispatch(request, *args, **kwargs)


class SignInUserLogIn(AuthView):
    form_class = UserLoginForm
    success_url = reverse_lazy('frontend:home')

    def get_success_url(self):
        success_url = force_text(self.request.GET.get('next', self.success_url))
        return success_url

    def form_valid(self, form):
        request = self.request
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        try:
            if '@' in username:
                username = Settings.objects.get(email__iexact=username).profile.username
            user = authenticate(username=username, password=password)

            if user:
                # Password matching and user found with authenticate
                login(request, user)
                messages.success(request, _("Welcome to Villages.io"))
                return super(SignInUserLogIn, self).form_valid(form)
            else:
                # Password wrong
                form.add_error(None, 'Username or Password is wrong')
                # messages.add_message(request, messages.ERROR, )
        except ObjectDoesNotExist:
            # messages.add_message(request, messages.WARNING, 'This user is not registered yet')
            form.add_error(None, 'This user is not registered yet')
        except Exception as e:
            # messages.add_message(request, messages.ERROR, "User not found")
            form.add_error(None, 'User not found')

        return super(SignInUserLogIn, self).form_invalid(form)


class SignInUserPreRegister(AuthView):
    form_class = PreRegistrationForm
    success_url = reverse_lazy('frontend:home-page')

    def form_valid(self, form):
        invited_email = form.cleaned_data['email']
        email_token = force_text(urlsafe_base64_encode(force_bytes(invited_email)))
        complete_register_url = reverse('accounts:sign_in_user:sign_in_complete_register')

        content = {
            'confirm_url': '{}?email_token={}'.format(complete_register_url, email_token)
        }
        send_mail_from_system('Please confirm your registration', invited_email, 'confirm_registration.txt', content)
        messages.success(self.request, _("We sent you confirmation email"))
        return super(SignInUserPreRegister, self).form_valid(form)


class SignInUserRegister(AuthView):
    form_class = RegistrationForm
    success_url = reverse_lazy('accounts:sign_in_user:edit_profile')

    # invitation = None
    # def get_invitation(self):
    #     """
    #     Get invitation code saved in session by invitation view (shown
    #     when clicking on invitation link).
    #     """
    #     invite_code = self.request.session.get(INVITE_CODE_KEY)
    #     register_invitation = self.invitation
    #     if not register_invitation:
    #         if invite_code:
    #             try:
    #                 register_invitation = Invitation.objects.get(code=invite_code)
    #             except Invitation.DoesNotExist:
    #                 pass
    #     return register_invitation

    def get_invited_email(self):
        email_token = self.request.GET['email_token']
        invited_email = force_text(urlsafe_base64_decode(email_token))
        return invited_email

    def check_token(self):
        status = False
        try:
            invited_email = self.get_invited_email()
            validate_email(invited_email)
            if not Settings.objects.filter(email__iexact=invited_email).exists():
                status = True
        except (MultiValueDictKeyError, UnicodeDecodeError, TypeError, ValidationError) as e:
            pass
        return status

    def form_valid(self, form):
        request = self.request
        form.cleaned_data['email'] = self.get_invited_email()
        profile = form.save(request.location, settings.LANGUAGE_CODE)
        subscribe_mailchimp(profile)

        # invitation = self.invitation
        # if invitation:
        #     if invitation:
        #         # Turn invitation into endorsement.
        #         Endorsement.objects.create(
        #             endorser=invitation.from_profile,
        #             recipient=profile,
        #             weight=invitation.endorsement_weight,
        #             text=invitation.endorsement_text)
        #         send_invitation_accepted_email(invitation, profile)
        #         invitation.delete()
        # else:
        # Let sharer know someone registered through their link.
        send_shared_link_registration_email(request, profile)

        # Auto login.
        user = authenticate(username=form.username, password=form.password)
        login(request, user)
        Location.clear_session(request)
        # Notifications.
        send_registration_email(profile)
        messages.info(request, MESSAGES['registration_done'])
        return super(SignInUserRegister, self).form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not self.check_token():
            messages.error(self.request, 'Invalid confirm link')
            return HttpResponseRedirect(reverse('frontend:home-page'))
        return super(SignInUserRegister, self).dispatch(request, *args, **kwargs)


@login_required
def edit_profile(request):
    profile = request.profile

    if request.method == 'POST':
        user_agent = get_user_agent(request)
        form = ProfileForm(request.POST, request.FILES, user_agent=user_agent, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, MESSAGES['profile_saved'])
            return HttpResponseRedirect(reverse('frontend:home'))
    else:
        form = ProfileForm(instance=profile)
    return django_render(request, 'new_templates/profile_edit.html', {'form': form})


def send_registration_email(profile):
    subject = _("Welcome to Villages.io")
    send_mail_from_system(subject, profile, 'registration_email.txt',
                          {'profile': profile})


def send_invitation_accepted_email(invitation, profile):
    "Let inviter know invitation has been accepted."
    subject = _("%s accepted your invitation to Villages") % profile
    send_mail_from_system(
        subject, invitation.from_profile, 'invitation_accepted_email.txt',
        {'profile': profile})


def send_shared_link_registration_email(request, profile):
    "Let sharer know someone registered through their link."
    sharer_id = request.session.get(SHARED_BY_PROFILE_ID_KEY)
    if sharer_id:
        # Sharer_id shouldn't go into session unless it's a valid ID, so no
        # need to catch invalid ID.
        sharer = Profile.objects.get(pk=sharer_id)
        subject = _("%s registered on Villages "
                    "using your shared link") % profile
        send_mail_from_system(
            subject, sharer, 'shared_link_registration_email.txt',
            {'profile': profile})
