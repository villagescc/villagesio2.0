from django.contrib import messages
from django.shortcuts import render
from categories.models import SubCategories
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from categories.subcategories_manager.forms import AddSubCategory, EditSubCategory
from django.db import transaction


def view_subcategories(request):
    subcategories = SubCategories.objects.all()
    return render(request, 'manage_subcategories.html', {'subcategories': subcategories})


def add_subcategory(request):
    if request.method == 'POST':
        if 'initial' in request.POST:
            form = AddSubCategory()
        else:
            form = AddSubCategory(request.POST)
            if form.is_valid():
                try:
                    subcategory = SubCategories()
                    subcategory.sub_categories_text = form.cleaned_data['sub_categories_text'].upper()
                    subcategory.categories_id = form.cleaned_data['category_filter'].id
                    subcategory.save()
                    messages.add_message(request, messages.SUCCESS, 'Category added with success')
                    return HttpResponseRedirect(reverse('categories:subcategories_manager:manage_subcategories'))
                except Exception:
                    messages.add_message(request, messages.ERROR, 'An error has occurred, please verify')
    else:
        form = AddSubCategory()
    return render(request, 'add_subcategory.html', {'form': form})


def edit_subcategory(request, category_id):
    subcategory = SubCategories.objects.get(id=category_id)
    if not subcategory:
        messages.add_message(request, messages.ERROR, 'No category has been found with this id')
        return HttpResponseRedirect(reverse('categories:subcategories_manager:manage_subcategories'))
    if request.method == 'POST':
        form = EditSubCategory(request.POST)
        if form.is_valid():
            try:
                if form.cleaned_data['categories_text'] == subcategory.categories_text:
                    messages.add_message(request, messages.ERROR, 'No changes were identified')
                else:
                    subcategory.categories_text = form.cleaned_data['categories_text']
                    subcategory.save()
                    messages.add_message(request, messages.SUCCESS, 'The category was successfully edited')
                    return HttpResponseRedirect(reverse('categories:subcategories_manager:manage_subcategories'))
            except Exception as e:
                messages.add_message(request, messages.ERROR, 'An error has occurred, please try again later.')

    else:
        form = EditSubCategory(initial={'sub_categories_text': subcategory.sub_categories_text,
                                        'category_filter': subcategory.categories.categories_text})
    return render(request, 'edit_category.html', {'form': form})


@transaction.atomic
def delete_subcategory(request):
    if request.method == 'POST' and request.is_ajax():
        subcategories_to_remove = SubCategories.objects.filter(id__in=[",".join(request.POST.getlist('ids[]'))])
        try:
            for subcategory in subcategories_to_remove:
                SubCategories.objects.filter(id=subcategory.id).delete()
        except Exception as e:
            messages.add_message(request, messages.ERROR, 'An error occurred, please try again later.')
    return HttpResponseRedirect(reverse('categories:subcategories_manager:manage_subcategories'))
