from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.shortcuts import render as django_render
from django.utils.translation import ugettext_lazy as _
from accounts.forms import UserForm
from profile.forms import RegistrationForm
from profile.models import Profile, Invitation, PasswordResetLink
from django.conf import settings
from django.contrib.auth import login, authenticate
from relate.models import Endorsement
from general.mail import send_mail_from_system
from general.util import render, deflect_logged_in
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as django_login
from geo.models import Location
from geo.util import location_required
from profile.forms import (
    RegistrationForm, ProfileForm, ContactForm, SettingsForm, InvitationForm,
    RequestInvitationForm, ForgotPasswordForm)
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.exceptions import ObjectDoesNotExist

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
    'invitation_landing': _("%s has invited you to Villages.cc. "
                            "Please take a look around and then use the "
                            "<em>Join</em> link on the right to register."),
    'password_link_sent': _("A password reset link has been emailed to you."),
    'password_reset': _("Your password has been reset. You may now log in "
                        "with your new password."),
}


def get_invitation(request):
    """
    Get invitation code saved in session by invitation view (shown
    when clicking on invitation link).
    """
    invitation = None
    invite_code = request.session.get(INVITE_CODE_KEY)
    if invite_code:
        try:
            invitation = Invitation.objects.get(code=invite_code)
        except Invitation.DoesNotExist:
            pass
    return invitation


class SignInUserLogIn(View):
    form_class = UserForm

    def get(self, request):
        form = self.form_class()
        form.fields.pop('first_name')
        form.fields.pop('email')
        return django_render(request, 'accounts/sign_in.html', {'form': form})

    def post(self, request):
        form = UserForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']

        try:
            if not '@' in username:
                user = User.objects.get(username=username)
                user = authenticate(username=username, password=password)
            else:
                user = User.objects.get(email=username)
                user = authenticate(username=user.username, password=password)
            if user:
                # Password matching and user found with authenticate
                login(request, user)
                return HttpResponseRedirect(reverse('frontend:home'))
            else:
                # Password wrong
                messages.add_message(request, messages.ERROR, 'Username or Password is wrong')
                return HttpResponseRedirect(reverse('accounts:sign_in_user:sign_in_log_in'))
        except ObjectDoesNotExist:
            form.fields.pop('first_name')
            form.fields.pop('email')
            messages.add_message(request, messages.WARNING, 'This user is not registered yet')
            return django_render(request, 'accounts/sign_in.html', {'form': form})
        except Exception as e:
            messages.add_message(request, messages.ERROR, " User not found")
            # return django_render(request, 'accounts/sign_in.html', {'form': form})
            return HttpResponseRedirect(reverse('accounts:sign_in_user:sign_in_log_in'))


class SignInUserRegister(View):
    form_class = RegistrationForm

    def get(self, request):
        if not request.location:
            return HttpResponseRedirect("%s?%s=%s" % (
                reverse('locator'), REDIRECT_FIELD_NAME, request.path))
        form = self.form_class()
        # form.fields.pop('new_password')
        return django_render(request, 'accounts/signup.html', {'form': form})

    def post(self, request):
        invitation = get_invitation(request)
        if settings.INVITATION_ONLY and not invitation:
            raise PermissionDenied
        if request.method == 'POST':
            form = RegistrationForm(request.POST)
            if form.is_valid():
                profile = form.save(request.location, settings.LANGUAGE_CODE)
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
                django_login(request, user)
                Location.clear_session(request)  # Location is in profile now.
                # Notifications.
                send_registration_email(profile)
                messages.info(request, MESSAGES['registration_done'])
                return HttpResponseRedirect(reverse('accounts:sign_in_user:edit_profile'))
            # else:
            #     messages.add_message(request, messages.ERROR, 'An error occurred, please contact an administrator.')
            #     return django_render(request, 'accounts/sign_in.html', {'form': form})
        else:
            initial = {}
            if invitation:
                initial['email'] = invitation.to_email
            form = RegistrationForm(initial=initial)
        return django_render(request, 'accounts/signup.html', {'form': form})

@login_required
@render()
def edit_profile(request):
    profile = request.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.info(request, MESSAGES['profile_saved'])
            return HttpResponseRedirect(reverse('my_profile'))
    else:
        form = ProfileForm(instance=profile)
    return locals()


def send_registration_email(profile):
    subject = _("Welcome to Villages.cc")
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

