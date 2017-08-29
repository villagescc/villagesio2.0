from django import forms
from django.core.exceptions import ValidationError
from categories.models import Categories, SubCategories


def check_duplicated_subcategory(value):
    categories_text = Categories.objects.filter(categories_text=value).first()
    if categories_text:
        raise ValidationError('There is already a category with this name.')


class AddSubCategory(forms.Form):

    category_filter = forms.ModelChoiceField(queryset=Categories.objects.all(),
                                             label='Category', required=True,
                                             widget=forms.Select(attrs={'class': 'form-control'}))

    sub_categories_text = forms.CharField(validators=[check_duplicated_subcategory], label='Subcategory', required=True,
                                          widget=forms.TextInput(attrs={'class': 'form-control'}))


class EditSubCategory(AddSubCategory):
    sub_categories_text = forms.CharField(required=False, max_length=50, min_length=2,
                                          widget=forms.TextInput(attrs={'class': 'form-control'}))


class FilterSubCategory(forms.Form):

    category_filter = forms.ModelChoiceField(queryset=Categories.objects.all(),
                                             label='Filter by category', required=True,
                                             widget=forms.Select(attrs={'class': 'form-control'}))