from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

from profile.models import Profile, Invitation, Settings, PasswordResetLink
from general.models import EmailField
from general.mail import send_mail, send_mail_to_admin
from general.util import rotate_image
from general.forms import ReceiverInput
from geo.util import build_location


alphanumeric = RegexValidator(r'^[0-9a-zA-Z_\s]*$', 'Only alphanumeric characters are allowed.')

ERRORS = {
    'email_dup': _("That email address is registered to another user."),
    'already_invited': _("You have already sent an invitation to %s."),
    'self_invite': _("You can't invite yourself."),
    'over_weight': _("Please ensure this number is below %d."),
    'invalid_username': _("That username or email isn't recognized."),
}


class PreRegistrationForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = ("email",)

    # def clean_email(self):
    #     email = self.cleaned_data['email']
    #     if Settings.objects.filter(email__iexact=email).exists():
    #         raise forms.ValidationError(ERRORS['email_dup'])
    #     return email


class RegistrationForm(UserCreationForm):
    # Parent class has username, password1, and password2.
    first_name = forms.CharField(
        max_length=100, required=False, label=_("Name"), help_text=_(
            "Name displayed to other users. You can change this later."),
        widget=forms.TextInput(attrs={}))

    password1 = forms.CharField(label="Password", help_text=_("Desired password."),
                                widget=forms.PasswordInput(attrs={}))

    password2 = forms.CharField(label="Password confirm", widget=forms.PasswordInput(attrs={}))

    # email = forms.EmailField(
    #     max_length=EmailField.MAX_EMAIL_LENGTH, label=_("Email"), help_text=_(
    #         "The address to receive notifications from Villages."),
    #     widget=forms.TextInput(attrs={}))
    terms_of_service = forms.BooleanField(label='I agree with terms of service', required=True,
                                          widget=forms.CheckboxInput(attrs={'style': 'width: auto; box-shadow:none;'}))

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = _(
            "Desired login name. You cannot change this.")
        self.fields['username'].widget = forms.TextInput(attrs={})
        self.fields['username'].validators = [alphanumeric]

    def clean_username(self):
        # Adapted from UserCreationForm.clean_username.
        # Make username uniqueness check case-insensitive.
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(
            _("A user with that username already exists."))

    def save(self, location, language):
        data = self.cleaned_data
        user = super(RegistrationForm, self).save(commit=False)
        user.last_login = timezone.now()
        user.email = data['email']
        user.first_name = data['first_name']
        # user.last_name = data['last_name']
        user.username = user.username.lower()
        user.save()
        profile = Profile(user=user, name=data.get('first_name', data['username']))
        if location:
            if not location.id:
                location.save()
        profile.location = location
        # profile.name = data['first_name'] + ' ' + data['last_name']
        profile.save()
        profile.settings.email = data['email']
        profile.settings.language = language
        profile.settings.feed_radius = -1
        profile.settings.save()
        return profile

    @property
    def username(self):
        return self.cleaned_data['username']

    @property
    def password(self):
        return self.cleaned_data['password1']


RegistrationForm.base_fields.keyOrder = [
    'first_name', 'email', 'username', 'password1', 'password2']


class ForgotPasswordForm(forms.Form):
    username_or_email = forms.CharField(label=_("Username or email"))

    def clean_username_or_email(self):
        """
        If username or email is known to the system, set self.profile to
        appropriate value.  If username or email is unknown, and raise
        ValidationError.
        """
        username_or_email = self.cleaned_data['username_or_email']
        try:
            user = User.objects.get(username__iexact=username_or_email)
            self.profile = user.profile
        except User.DoesNotExist:
            try:
                self.profile = Profile.objects.get(
                    settings__email__iexact=username_or_email)
            except Profile.DoesNotExist:
                raise forms.ValidationError(ERRORS['invalid_username'])
        return username_or_email

    def create_reset_link(self):
        link = PasswordResetLink(profile=self.profile)
        link.save()
        link.send()


class InvitationForm(forms.ModelForm):
    # TODO: Merge with EndorseForm somehow, into a common superclass?

    class Meta:
        model = Invitation
        fields = ('to_email', 'message', 'endorsement_weight',
                  'endorsement_text')

    def __init__(self, from_profile, *args, **kwargs):
        self.from_profile = from_profile
        super(InvitationForm, self).__init__(*args, **kwargs)
        self.fields['endorsement_weight'].widget = (
            forms.TextInput(attrs={'class': 'int spinner'}))
        self.fields['endorsement_weight'].min_value = 1        

    def clean_to_email(self):
        to_email = self.cleaned_data['to_email']
        if Invitation.objects.filter(
            from_profile=self.from_profile, to_email__iexact=to_email).exists():
            raise forms.ValidationError(ERRORS['already_invited'] % to_email)
        if to_email.lower() == self.from_profile.email.lower():
            raise forms.ValidationError(ERRORS['self_invite'])
        return to_email

    @property
    def max_weight(self):
        if not self.from_profile.endorsement_limited:
            return None
        max_weight = self.from_profile.endorsements_remaining
        if self.instance.id:
            max_weight += self.instance.weight
        return max_weight

    def clean_endorsement_weight(self):
        weight = self.cleaned_data['endorsement_weight']
        if self.from_profile.endorsement_limited and weight > self.max_weight:
            raise forms.ValidationError(
                ERRORS['over_weight'] % self.max_weight)
        return weight

    def save(self):
        invitation = super(InvitationForm, self).save(commit=False)
        invitation.from_profile = self.from_profile
        invitation.save()
        return invitation


class RequestInvitationForm(forms.Form):
    name = forms.CharField(required=False)
    email = forms.EmailField(max_length=EmailField.MAX_EMAIL_LENGTH)
    text = forms.CharField(widget=forms.Textarea, label="Why I want to join")

    def sender(self):
        "Returns appropriate text for email sender field."
        data = self.cleaned_data
        return data.get('name'), data['email']

    def send(self, to_profile=None):
        data = self.cleaned_data
        subject = "Villages.io Invitation Request"
        context = {'text': data['text'],
                   'email': data['email']}
        if to_profile:
            send_mail(subject, self.sender(), to_profile,
                      'request_invitation_email.txt', context)
        else:
            send_mail_to_admin(
                subject, self.sender(), 'request_invitation_email.txt', context)


class ProfileForm(forms.ModelForm):
    location = forms.CharField(required=False)

    class Meta:
        model = Profile
        fields = ('name', 'photo', 'header_image', 'job', 'description')

        widgets = {
            'name': forms.TextInput(attrs={'style': 'width: 100%'}),
            'description': forms.Textarea(attrs={'style': 'height: 150px;'}),
            # 'job': forms.TextInput(attrs={}),
        }

    def __init__(self, *args, **kwargs):
        self.user_agent = kwargs.pop('user_agent', None)
        super(ProfileForm, self).__init__(*args, **kwargs)

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        new_photo = self.files.get('photo')
        if new_photo:
            user_agent = self.user_agent
            if user_agent and (user_agent.device.family == 'iPhone' or user_agent.device.family == 'iPad'):
                photo = rotate_image(new_photo)
        return photo

    def clean_header_image(self):
        header_image = self.cleaned_data.get('header_image')
        new_header_image = self.files.get('header_image')
        if new_header_image:
            user_agent = self.user_agent
            if user_agent and (user_agent.device.family == 'iPhone' or user_agent.device.family == 'iPad'):
                header_image = rotate_image(new_header_image)
        return header_image

    def save(self, commit=True):
        location = self.cleaned_data.get('location')
        if location:
            self.instance.location = build_location(location)
        self.instance.set_updated()
        return super(ProfileForm, self).save(commit)


class ContactForm(forms.Form):
    contact_recipient_name = forms.CharField(label='Recipients Name', required=True,
                                             widget=ReceiverInput(attrs={'class': 'typeahead'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'style': 'max-width: 100%; height:100px;'}))

    def send(self, sender, recipient, subject=None,
             template='contact_email.txt', extra_context=None):
        if not subject:
            subject = _("Villages.io message from %s") % sender
        context = {'message': self.cleaned_data['message'],
                   'sender': sender}
        if extra_context:
            context.update(extra_context)
        send_mail(subject, sender, recipient, template, context)


class SettingsForm(forms.ModelForm):

    # username = forms.CharField(required=True, max_length=30, validators=[alphanumeric],
    #                            widget=forms.TextInput(attrs={'class': 'form-control'}))
    # Email is required.
    email = forms.EmailField(widget=forms.EmailInput(),
                             max_length=EmailField.MAX_EMAIL_LENGTH)

    # endorsement_limited = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Settings
        fields = ('email', 'send_notifications', 'send_newsletter', 'feed_radius', 'language')

        widgets = {
            'language': forms.Select(attrs={
                'style': 'width: 100%',
            }),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if Settings.objects.filter(email__iexact=email).exclude(
                pk=self.instance.id).exists():
            raise forms.ValidationError(ERRORS['email_dup'])
        return email


class FormProfileTag(forms.Form):

    tag = forms.CharField(required=False,
                          widget=forms.TextInput(attrs={
                              'style': 'width: 100%',
                              'data-role': 'tagsinput'}))
