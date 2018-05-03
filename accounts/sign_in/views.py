from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.views.generic.edit import FormView
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render as django_render
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from django_user_agents.utils import get_user_agent

from accounts.forms import UserLoginForm
from profile.models import Profile, Invitation
from relate.models import Endorsement
from general.mail import send_mail_from_system
from profile.models import Settings
from geo.models import Location
from profile.forms import RegistrationForm, ProfileForm

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

    api = mailchimp.Mailchimp(API_KEY)
    try:
        api.lists.subscribe(LIST_ID, {'name': profile.name,
                                      'email': profile.settings.email,
                                      'zipcode': postal_code if postal_code else ''},
                            send_welcome=False, double_optin=False)
    except Exception as e:
        print(e)

    return


class AuthView(FormView):

    def get_success_url(self):
        next_url = self.request.GET.get('next', reverse('frontend:home'))
        return next_url

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(self.get_success_url())
        return super(AuthView, self).get(request, *args, **kwargs)

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super(AuthView, self).dispatch(request, *args, **kwargs)


class SignInUserLogIn(AuthView):
    template_name = 'new_templates/sign_in.html'
    form_class = UserLoginForm

    def form_valid(self, form):
        request = self.request
        username = form.username
        password = form.password
        try:
            if '@' in username:
                username = Settings.objects.get(email__iexact=username).profile.username
            user = authenticate(username=username, password=password)

            if user:
                # Password matching and user found with authenticate
                login(request, user)
                return super(SignInUserLogIn, self).form_valid(form)
            else:
                # Password wrong
                messages.add_message(request, messages.ERROR, 'Username or Password is wrong')
        except ObjectDoesNotExist:
            messages.add_message(request, messages.WARNING, 'This user is not registered yet')
        except Exception as e:
            messages.add_message(request, messages.ERROR, " User not found")

        return super(SignInUserLogIn, self).form_invalid(form)


class SignInUserRegister(AuthView):
    template_name = 'new_templates/sign_up.html'
    form_class = RegistrationForm
    invitation = None

    def get_invitation(self):
        """
        Get invitation code saved in session by invitation view (shown
        when clicking on invitation link).
        """
        invite_code = self.request.session.get(INVITE_CODE_KEY)
        register_invitation = self.invitation
        if not register_invitation:
            if invite_code:
                try:
                    register_invitation = Invitation.objects.get(code=invite_code)
                except Invitation.DoesNotExist:
                    pass
        return register_invitation

    def form_valid(self, form):
        request = self.request

        profile = form.save(request.location, settings.LANGUAGE_CODE)
        invitation = self.invitation
        if invitation:
            if invitation:
                # Turn invitation into endorsement.
                Endorsement.objects.create(
                    endorser=invitation.from_profile,
                    recipient=profile,
                    weight=invitation.endorsement_weight,
                    text=invitation.endorsement_text)
                send_invitation_accepted_email(invitation, profile)
                invitation.delete()
        else:
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
        self.invitation = self.get_invitation()
        if settings.INVITATION_ONLY and not self.invitation:
            raise PermissionDenied
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
