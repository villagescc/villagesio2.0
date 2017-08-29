from django import forms
from django.conf import settings


class FormSearchUsers(forms.Form):

    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Search users'
    }))