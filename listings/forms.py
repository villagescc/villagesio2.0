from django.forms import ModelForm
from django import forms

# Import App Model
from listings.models import Listings
from categories.models import SubCategories, Categories


# Forms
class ListingsForms(ModelForm):

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

    price = forms.DecimalField(label='Price (In Village Hours ?)',
                               widget=forms.NumberInput(attrs={
                               }))

    class Meta:
        model = Listings
        fields = ['listing_type', 'title', 'description', 'price', 'categories', 'subcategories', 'photo', 'tag']
        widgets = {
            # 'listing_type': Select(attrs={
            #     'class': 'form-control',
            #     'style': 'width: 100%;'
            # }),
            # 'title': forms.TextInput(attrs={
            #     'class': 'form-control',
            #     'style': 'width: 100%',
            # }),
            'description': forms.Textarea(attrs={
            }),
            # 'subcategories': Select(attrs={
            #     'class': 'form-control'
            # }),
            'photo': forms.FileInput()
        }


