from datetime import datetime
from django.forms import ModelForm
from django.forms.widgets import Select, NumberInput
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from listings.models import Listings

INFINITE_RADIUS = -1

RADIUS_CHOICES = (
    (1000, _('Within 1 km')),
    (5000, _('Within 5 km')),
    (10000, _('Within 10 km')),
    (50000, _('Within 50 km')),
    (INFINITE_RADIUS, _('Anywhere')),
)

RADII = [rc[0] for rc in RADIUS_CHOICES]
DEFAULT_RADIUS = 5000
DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%f'


class FormListingsSettings(forms.Form):

    d = forms.DateTimeField(
        label="Up to date", required=False, input_formats=[DATE_FORMAT])

    trusted = forms.BooleanField(label='Trusted only', required=False,
                                 widget=forms.CheckboxInput(attrs={
                                     'class': 'form-control checkbox-inline',
                                     'style': 'vertical-align: middle; width: 15px;'
                                 }))

    q = forms.CharField(label='Search', required=False,
                        widget=forms.TextInput(attrs={
                            'placeholder': 'Search posts...'}))

    radius = forms.TypedChoiceField(
        required=False, choices=RADIUS_CHOICES, coerce=int, empty_value=None,
        widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, data, profile, location=None, type_filter=None, *args, **kwargs):
        self.profile, self.location, self.type_filter, self.listing_type = (profile, location, type_filter, data.get('listing_type'))
        data = data.copy()
        if 'radius' not in data:
            default_radius = (profile and profile.settings.feed_radius or DEFAULT_RADIUS)
            data['radius'] = default_radius
            self._explicit_radius = False
        else:
            self._explicit_radius = True
        super(FormListingsSettings, self).__init__(data, *args, **kwargs)

    def get_results(self):
        data = self.cleaned_data
        date = data.get('d') or datetime.now()
        tsearch = data.get('q')
        radius = data['radius']
        query_radius = radius
        if radius == INFINITE_RADIUS:
            query_radius = None
        trusted = data['trusted']
        while True:
            items, count = Listings.objects.get_items_and_remaining(location=self.location, tsearch=tsearch,
                                                                    trusted_only=trusted, radius=query_radius,
                                                                    up_to_date=date, request_profile=self.profile,
                                                                    type_filter=self.type_filter,
                                                                    listing_type=self.listing_type)
            if (not (self.profile and self.profile.settings.feed_radius) and
                not self._explicit_radius and
                len(items) < settings.LISTING_ITEMS_PER_PAGE and query_radius != None):
                query_radius = next_query_radius(query_radius)
                self.data['radius'] = query_radius
                if query_radius == INFINITE_RADIUS:
                    query_radius = None
                continue
            break
        return items, count

    def update_sticky_filter_prefs(self):
        """
        Save radius and trusted filter values as sticky prefs to profile
        settings.
        """
        if not self.profile:
            return
        data = self.cleaned_data
        radius = data['radius']
        trusted = data['trusted']
        save_settings = False
        if radius != self.profile.settings.feed_radius:
            self.profile.settings.feed_radius = radius
            save_settings = True
        if trusted != self.profile.settings.feed_trusted:
            self.profile.settings.feed_trusted = trusted
            save_settings = True
        if save_settings:
            self.profile.settings.save()


def next_query_radius(radius):
    i = RADII.index(radius)
    return RADII[i + 1]