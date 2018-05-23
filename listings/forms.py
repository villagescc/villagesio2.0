from django import forms

from listings.models import Listings
from categories.models import SubCategories, Categories
from general.util import rotate_image
from general.forms import PhotoInput


class ListingsForms(forms.ModelForm):
    categories = forms.ModelChoiceField(queryset=Categories.objects.all(),
                                        required=False, label='Category',
                                        widget=forms.Select(attrs={}))

    subcategories = forms.ModelChoiceField(queryset=SubCategories.objects.all(),
                                           label='Sub-category', required=False,
                                           widget=forms.Select(attrs={}))

    tag = forms.CharField(required=False, label='Tags',
                          widget=forms.TextInput(attrs={
                              'data-role': 'tagsinput',
                              'title': "Tags are used to match you with other people - (Separate tags with commas ',')"}))

    price = forms.DecimalField(label='Price (In Village Hours ?)')

    class Meta:
        model = Listings
        fields = ['listing_type', 'title', 'description', 'price', 'categories', 'subcategories', 'photo', 'tag']
        widgets = {
            'description': forms.Textarea(),
            'photo': PhotoInput(),
        }

    def __init__(self, *args, **kwargs):
        self.user_agent = kwargs.pop('user_agent', None)
        super(ListingsForms, self).__init__(*args, **kwargs)

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        new_photo = self.files.get('photo')
        if new_photo:
            user_agent = self.user_agent
            if user_agent and (user_agent.device.family == 'iPhone' or user_agent.device.family == 'iPad'):
                photo = rotate_image(new_photo)
        return photo
