from datetime import datetime

from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login as django_login
from django.contrib.auth.views import login as django_login_view
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.utils import translation
from django.shortcuts import render as django_render
from django.utils.translation import ugettext_lazy as _

from listings.models import Listings
from listings.views import update_profile_tags
from relate.forms import AcknowledgementForm, EndorseForm
from tags.models import Tag
from accounts.forms import UserForm
from profile.forms import RegistrationForm, ProfileForm, ContactForm, SettingsForm, InvitationForm, \
    RequestInvitationForm, ForgotPasswordForm, FormProfileTag
from profile.models import Profile, Invitation, PasswordResetLink, ProfilePageTag
from relate.models import Referral
from post.models import Post
from geo.util import location_required
from geo.models import Location
from relate.models import Endorsement
from feed.views import feed
from general.util import render, deflect_logged_in
from general.mail import send_mail_from_system
from listings.forms import ListingsForms

# Session key to store invite code for later signing up.
INVITE_CODE_KEY = 'invite_code'

# Session key for profile ID of link sharer.
SHARED_BY_PROFILE_ID_KEY = 'shared_by'

MESSAGES = {
    'profile_saved': _("Profile saved."),
    'contact_sent': _("Message sent."),
    'registration_done': _("Thank you for registering.<br><br>"
                          "Please continue filling out your profile by "
                          "uploading a photo and describing yourself for other "
                          "users.<br><br>"
                          "We have sent a welcome email to your address. "
                          "If you do not receive it, please verify your email "
                          "address under account settings."),
    'password_changed': _("Password changed."),
    'settings_changed': _("Settings saved."),
    'email_updated': _("Settings saved.<br><br>"
                      "A confirmation email has been sent to your new address. "
                      "If you do not receive it, please verify that you have "
                      "entered the correct email."),
    'invitation_sent': _("Invitation sent to %s."),
    'invitation_deleted': _("Invitation deleted."),
    'invitation_request_sent': _("Invitation request sent."),
    'invitation_landing': _("%s has invited you to Villages.<br>"
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


@deflect_logged_in
def check_invitation(request):
    """
    Check for invitation in session before proceeding to registration.
    If no invitation, redirect to request_invitation.
    """
    invitation = get_invitation(request)
    if invitation or not settings.INVITATION_ONLY:
        return redirect(register)
    else:
        return redirect(request_invitation)


@deflect_logged_in
@location_required
@render()
def register(request):
    """
    Registration form.
    """
    invitation = get_invitation(request)
    if settings.INVITATION_ONLY and not invitation:
        raise PermissionDenied    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            profile = form.save(request.location, request.LANGUAGE_CODE)
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
            return redirect(edit_profile)
    else:
        initial = {}
        if invitation:
            initial['email'] = invitation.to_email
        form = RegistrationForm(initial=initial)
    return locals()


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


@deflect_logged_in
def login(request):
    response = django_login_view(
        request, template_name='login.html', redirect_field_name='next')
    # Don't redirect to locator view upon login.
    if (isinstance(response, HttpResponseRedirect) and
        response['Location'] == reverse('locator')):
        return redirect('home')
    return response


@deflect_logged_in
@render()
def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        sign_in_form = UserForm()
        sign_in_form.fields.pop('first_name')
        sign_in_form.fields.pop('email')
        if form.is_valid():
            form.create_reset_link()
            messages.info(request, MESSAGES['password_link_sent'])
            return django_render(request, 'accounts/sign_in.html', {'form': sign_in_form})
    else:
        form = ForgotPasswordForm()
    return locals()


@deflect_logged_in
@render()
def reset_password(request, code):
    link = get_object_or_404(
        PasswordResetLink, code=code, expires__gt=datetime.now())
    if request.method == 'POST':
        form = SetPasswordForm(link.profile.user, request.POST)
        if form.is_valid():
            form.save()
            link.delete()
            messages.info(request, MESSAGES['password_reset'])
            return HttpResponseRedirect(reverse('accounts:sign_in_user:sign_in_log_in'))
    else:
        form = SetPasswordForm(link.profile.user)
    return locals()


@login_required
def edit_settings(request):
    request.session['from_settings'] = True
    # social_auth = request.user.social_auth.filter(provider="facebook")
    if request.method == 'POST':
        if 'change_settings' in request.POST:
            old_email = request.profile.settings.email
            settings_form = SettingsForm(request.POST, instance=request.profile.settings)
            if settings_form.is_valid():
                settings_obj = settings_form.save()
                translation.activate(settings_obj.language)
                request.session['django_language'] = translation.get_language()
                if settings_obj.email != old_email:
                    send_new_address_email(settings_obj)
                    messages.info(request, MESSAGES['email_updated'])
                else:
                    messages.info(request, MESSAGES['settings_changed'])
                return redirect(edit_settings)
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.info(request, MESSAGES['password_changed'])
                return redirect(edit_settings)
        
    if 'change_settings' not in request.POST:
        settings_form = SettingsForm(instance=request.profile.settings)
    if 'change_password' not in request.POST:
        password_form = PasswordChangeForm(request.user)

    return django_render(request, 'new_templates/profile_settings.html', {'settings_form': settings_form,
                                                                          'password_form': password_form})


def send_new_address_email(settings_obj):
    subject = _("Your Villages.io email address has been updated")
    send_mail_from_system(subject, settings_obj.profile, 'new_email.txt',
                          {'new_email': settings_obj.email})


@login_required
@render()
def edit_profile(request):
    profile = request.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.info(request, MESSAGES['profile_saved'])
            return HttpResponseRedirect(reverse(my_profile))
    else:
        form = ProfileForm(instance=profile)
    return HttpResponseRedirect(reverse('my_profile'))

# @login_required()
# def edit_tags(request):
#     tags = request.profile.tags.all()
#     return django_render(request, 'profile_tag_management.html', {'form': form,
#                                                                   'tags': tags})


@login_required
def my_profile(request):

    offer_tags = []
    request_tags = []
    teach_tags = []
    learn_tags = []
    other_tags = []

    listing_form = ListingsForms()
    listings = Listings.objects.filter(user_id=request.profile.user_id).order_by('-id')
    endorsements_received = request.profile.endorsements_received.all()
    endorsements_made = request.profile.endorsements_made.all()
    profile_tags = ProfilePageTag.objects.filter(profile_id=request.profile.id)

    for each_profile_tag in profile_tags:
        if each_profile_tag.listing_type == 'OFFER':
            offer_tags.append(each_profile_tag)
        elif each_profile_tag.listing_type == 'REQUEST':
            request_tags.append(each_profile_tag)
        elif each_profile_tag.listing_type == 'TEACH':
            teach_tags.append(each_profile_tag)
        elif each_profile_tag.listing_type == 'LEARN':
            learn_tags.append(each_profile_tag)
        else:
            other_tags.append(each_profile_tag)

    referral_obj_list = []
    referral_count = []
    referral = Referral.objects.filter(recipient=request.profile)
    for each_referral in referral:
        referral_obj_list.append(each_referral.referrer)
    trusting_profiles = request.profile.trusted_profiles.through.objects.filter(
        from_profile_id=request.profile.id)

    if trusting_profiles:
        for each_trusting in trusting_profiles:
            if each_trusting.to_profile in referral_obj_list:
                referral_count.append(each_trusting.to_profile)

    if referral_count:
        referral_count = len(referral_count)
    else:
        referral_count = None

    return django_render(request, 'new_templates/my_profile.html',
                         {'profile': request.profile, 'listings': listings, 'endorsements_made': endorsements_made,
                          'endorsements_received': endorsements_received, 'offer_tags': offer_tags,
                          'request_tags': request_tags, 'teach_tags': teach_tags, 'learn_tags': learn_tags,
                          'other_tags': other_tags, 'listing_form': listing_form, 'referral': referral,
                          'referral_count': referral_count})


@render()
@login_required
def profile(request, username):

    offer_tags = []
    request_tags = []
    teach_tags = []
    learn_tags = []
    other_tags = []

    endorsement = None
    profile = get_object_or_404(Profile, user__username=username)
    if profile == request.profile:
        return HttpResponseRedirect(reverse(my_profile))
    else:
        listing_form = ListingsForms()
        template = 'profile.html'
        if request.profile:
            profile_endorsements_made = profile.endorsements_made.all()
            profile_endorsements_received = profile.endorsements_received.all()
            account = profile.account(request.profile)
            trust_form = EndorseForm(instance=endorsement, endorser=None, recipient=None)
            payment_form = AcknowledgementForm(max_ripple=None, initial=request.GET)
            listings = Listings.objects.filter(user_id=profile.user_id).order_by('-id')
            contact_form = ContactForm()

            profile_tags = ProfilePageTag.objects.filter(profile_id=profile.id)

            for each_profile_tag in profile_tags:
                if each_profile_tag.listing_type == 'OFFER':
                    offer_tags.append(each_profile_tag)
                elif each_profile_tag.listing_type == 'REQUEST':
                    request_tags.append(each_profile_tag)
                elif each_profile_tag.listing_type == 'TEACH':
                    teach_tags.append(each_profile_tag)
                elif each_profile_tag.listing_type == 'LEARN':
                    learn_tags.append(each_profile_tag)
                else:
                    other_tags.append(each_profile_tag)

            referral = Referral.objects.filter(recipient=profile)
            if referral:
                referral_count = referral.count()
            else:
                referral_count = None

            return django_render(request, 'new_templates/profile.html',
                                 {'endorsements_made': profile_endorsements_made,
                                  'endorsements_received': profile_endorsements_received,
                                  'account': account, 'listing_form': listing_form, 'profile': profile,
                                  'trust_form': trust_form, 'payment_form': payment_form, 'contact_form': contact_form,
                                  'offer_tags': offer_tags, 'request_tags': request_tags, 'teach_tags': teach_tags,
                                  'learn_tags': learn_tags, 'other_tags': other_tags, 'listings': listings,
                                  'referral': referral, 'referral_count': referral_count})
    return locals(), template


# TODO: Move to post app?
def profile_posts(request, username):
    profile = get_object_or_404(Profile, user__username=username)
    if profile == request.profile:
        template = 'my_posts.html'
        extra_context = {}
    else:
        template = 'profile_posts.html'
        extra_context = {'profile': profile}
    return feed(request, item_type=Post, poster=profile, template=template,
                extra_context=extra_context)

# TODO: Move to relate app?
@login_required
def profile_endorsements(request, username):
    eligible_profiles = Profile.objects.exclude(pk=request.profile.id)
    profile = get_object_or_404(
        eligible_profiles, user__username=username)
    return feed(request, item_type=Endorsement, recipient=profile,
                template='profile_endorsements.html',
                extra_context={'profile': profile})


def contact(request, username):
    profile = get_object_or_404(Profile, user__username=username)
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.send(sender=request.profile, recipient=profile)
            messages.info(request, MESSAGES['contact_sent'])
            return redirect(profile, (username,))
    else:
        form = ContactForm()
    return locals()


@login_required
def undefined_contact(request):
    if request.method == 'GET':
        recipient_name = request.GET.get('recipient_name')
        form = ContactForm(initial={'contact_recipient_name': recipient_name})
        if recipient_name:
            try:
                Profile.objects.exclude(user=request.user).get(user__username=recipient_name)
            except Profile.DoesNotExist:
                form.errors['contact_recipient_name'] = "Recipient doesn't exist."

    elif request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            recipient_name = form.cleaned_data['contact_recipient_name']
            try:
                recipient = Profile.objects.exclude(user=request.user).get(user__username=recipient_name)
            except Profile.DoesNotExist:
                form.add_error('contact_recipient_name', "Recipient doesn't exist.")
            else:
                listing_id = request.GET.get('listing_id')
                subject = None
                if listing_id:
                    listing_title = Listings.objects.filter(id=listing_id, profile=recipient)\
                        .values_list('title', flat=True).first()
                    if listing_title:
                        subject = 'In reply to Villages.io post: {}'.format(listing_title)

                form.send(sender=request.profile, recipient=recipient, subject=subject)
                messages.add_message(request, messages.SUCCESS, 'Message successfully sent.')
                form = ContactForm()

    return django_render(request, 'new_templates/contact.html', {'form': form})


@login_required
@render()
def invite(request):
    if request.method == 'POST':
        form = InvitationForm(request.profile, request.POST)
        if form.is_valid():
            
            # TODO: Check for email belonging to existing user,
            # call endorse_user(request), make sure it works.
            
            invitation = form.save()
            invitation.send()
            messages.info(request, MESSAGES['invitation_sent'] % (
                    invitation.to_email))
            return redirect(invite)
    else:
        initial = {'to_email': request.GET.get('email', '')}
        form = InvitationForm(request.profile, initial=initial)
    return locals()


@deflect_logged_in
@render()
def invitation(request, code):
    """
    Saves invitation code to session so user can register later and
    redirects to intro page with a message reflecting invite.
    """
    try:
        invitation = Invitation.objects.get(code=code)
    except Invitation.DoesNotExist:
        invitation = None
    if invitation is None:
        return {}, 'bad_invite_code.html'

    # TODO: Allow logged in users to convert an invitation to an endorsement.
    
    request.session[INVITE_CODE_KEY] = code
    messages.info(request, MESSAGES['invitation_landing'] % (
            invitation.from_profile))
    return redirect('home')


@login_required
@render()
def invitations_sent(request):
    '''
    If you already sent an invitation, when you try to send it again through "invitations sent"
    this is the method that does that
    :param request:
    :return:
    '''
    if request.method == 'POST':
        # Keys of interest in request.POST are be 'resend_NNN' and 'delete_NNN',
        # where NNN is the invitation ID to act on.
        key = None
        for k in request.POST.keys():
            if k.startswith('resend') or k.startswith('delete'):
                key = k
                break
        if key is None:
            raise Exception("Missing resend or delete parameter.")
        invitation_id = key.split('_')[1]
        invitation = get_object_or_404(
            request.profile.invitations_sent, pk=invitation_id)
        if key.startswith('resend'):
            invitation.send()
            messages.info(request, MESSAGES['invitation_sent'] %
                          invitation.to_email)
        elif key.startswith('delete'):
            invitation.delete()
            messages.info(request, MESSAGES['invitation_deleted'])
        return redirect(invitations_sent)
    invitations = request.profile.invitations_sent.order_by('-date')
    return locals()


@deflect_logged_in
@render()
def request_invitation(request):
    if request.method == 'POST':
        form = RequestInvitationForm(request.POST)
        if form.is_valid():
            to_profile = get_shared_by_profile(request)
            form.send(to_profile)
            messages.info(request, MESSAGES['invitation_request_sent'])
            return redirect('home')
    else:
        form = RequestInvitationForm()
    return locals()


def get_shared_by_profile(request):
    profile = None
    if SHARED_BY_PROFILE_ID_KEY in request.session:
        try:
            profile = Profile.objects.get(
                pk=request.session[SHARED_BY_PROFILE_ID_KEY])
        except Profile.DoesNotExist:
            pass
    return profile


@login_required
@render()
def share(request):
    return locals()


@login_required()
def add_profile_tag(request):
    if request.method == 'POST':
        tag_form = FormProfileTag(request.POST)
        if tag_form.is_valid():
            if request.POST.get('tag'):
                tags_to_add = request.POST.get('tag').split(',')
                for tag in tags_to_add:
                    new_tag = Tag(name=tag.lower())
                    try:
                        new_tag.save()
                        update_profile_tags(new_tag, request.profile)
                    except IntegrityError as e:
                        existing_tag = Tag.objects.get(name=tag)
                        update_profile_tags(existing_tag, request.profile)
        return django_render(request, 'profile_tag_management.html', {'tag_form': tag_form})
    else:
        profile_tags = ProfilePageTag.objects.filter(profile_id=request.profile.id)
        tag_form = FormProfileTag()
        return django_render(request, 'profile_tag_management.html', {'tag_form': tag_form,
                                                                      'profile_tags': profile_tags})


@login_required()
def delete_profile_tags(request):
    if request.method == 'POST' and request.is_ajax():
        list_tags_to_remove = []
        for tag_id in request.POST.getlist('ids[]'):
            list_tags_to_remove.append(int(tag_id))
        tags_to_remove = Tag.objects.filter(id__in=list_tags_to_remove)
        try:
            for tag in tags_to_remove:
                try:
                    ProfilePageTag.objects.filter(id=tag.id).delete()
                except Exception as e:
                    print(e)
        except Exception as e:
            messages.add_message(request, messages.ERROR, 'An error occurred, please try again later.')
    return HttpResponseRedirect(reverse('add_profile_tags'))
