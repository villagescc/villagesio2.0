from django import forms
from django.core.exceptions import ValidationError
from categories.models import Categories


def check_duplicated_category(value):
    categories_text = Categories.objects.filter(categories_text=value).first()
    if categories_text:
        raise ValidationError('There is already a category with this name.')


class AddCategory(forms.Form):
    categories_text = forms.CharField(validators=[check_duplicated_category], label='Category Name', required=True,
                                      widget=forms.TextInput(attrs={'class': 'form-control'}))


class EditCategory(AddCategory):
    categories_text = forms.CharField(required=False, max_length=50, min_length=2,
                                      widget=forms.TextInput(attrs={'class': 'form-control'}))


class FilterCategory(forms.Form):

    category_filter = forms.ModelChoiceField(queryset=Categories.objects.all(),
                                             label='Filter by category', required=True,
                                             widget=forms.Select(attrs={'class': 'form-control'}))