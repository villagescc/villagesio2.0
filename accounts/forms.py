from django.forms import ModelForm, Form
from django.contrib.auth.models import User
from django import forms

# App model
from profile.models import Profile

# Forms


class RegisterForm(ModelForm):
    """ Signup form """

    username = forms.CharField(max_length=30, required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))

    terms_of_service = forms.BooleanField(label='I agree with terms of service', required=True,
                                          widget=forms.CheckboxInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        # Overriding form to set email is required because User email is optional
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class UserForm(ModelForm):
    """
    User form to update the user information in the settings page
    """

    username = forms.CharField(widget=forms.TextInput(attrs={'style': 'width:auto;',
                                                             'placeholder': 'Email or username'}))

    password = forms.CharField(widget=forms.PasswordInput(attrs={'style': 'width:auto;', 'placeholder': 'Password'}))

    class Meta:
        model = User
        fields = ['first_name', 'username', 'email']


class UserLoginForm(Form):
    username = forms.CharField(label='EMAIL | USERNAME',
                               widget=forms.TextInput(attrs={'style': 'width:auto;',
                                                             'placeholder': 'Email or username'}))

    password = forms.CharField(widget=forms.PasswordInput(attrs={'style': 'width:auto;', 'placeholder': 'Password'}))
    device_id = forms.CharField(label='', widget=forms.HiddenInput(), required=False)


class ProfileCreationForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['user']


class ProfileSettingsForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['photo']
