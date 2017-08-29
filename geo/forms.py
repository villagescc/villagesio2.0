from django import forms
from django.utils.translation import ugettext_lazy as _
from geo.models import Location


class LocationForm(forms.ModelForm):

    class Meta:
        model = Location
        fields = ('neighborhood', 'city', 'state', 'country', 'point')

    set_home = forms.BooleanField(
        required=False, initial=True, label=_("Save as Home Location"))
        
    def __init__(self, *args, **kwargs):
        hide_set_home = kwargs.pop('hide_set_home', False)
        super(LocationForm, self).__init__(*args, **kwargs)
        if hide_set_home:
            del self.fields['set_home']
        self.fields['point'].widget = forms.HiddenInput()
        self.fields['neighborhood'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['city'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['state'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['country'].widget = forms.TextInput(attrs={'class': 'form-control'})
