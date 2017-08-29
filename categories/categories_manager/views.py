from categories.models import Categories, SubCategories
from categories.categories_manager.forms import AddCategory, EditCategory
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db import transaction


def view_categories(request):
    categories = Categories.objects.all()
    return render(request, 'manage_categories.html', {'categories': categories})


def add_category(request):
    if request.method == 'POST':
        if 'initial' in request.POST:
            form = AddCategory()
        else:
            form = AddCategory(request.POST)
            if form.is_valid():
                try:
                    category = Categories()
                    category.categories_text = form.cleaned_data['categories_text']
                    category.save()
                    messages.add_message(request, messages.SUCCESS, 'Category added with success')
                    return HttpResponseRedirect(reverse('categories:categories_manager:manage_categories'))
                except Exception:
                    messages.add_message(request, messages.ERROR, 'An error has occurred, please verify')
    else:
        form = AddCategory()
    return render(request, 'add_category.html', {'form': form})


def edit_category(request, category_id):
    category = Categories.objects.get(id=category_id)
    if not category:
        messages.add_message(request, messages.ERROR, 'No category has been found with this id')
        return HttpResponseRedirect(reverse('categories:categories_manager:manage_categories'))
    if request.method == 'POST':
        form = EditCategory(request.POST)
        if form.is_valid():
            try:
                if form.cleaned_data['categories_text'] == category.categories_text:
                    messages.add_message(request, messages.ERROR, 'No changes were identified')
                else:
                    category.categories_text = form.cleaned_data['categories_text']
                    category.save()
                    messages.add_message(request, messages.SUCCESS, 'The category was successfully edited')
                    return HttpResponseRedirect(reverse('categories:categories_manager:manage_categories'))
            except Exception as e:
                messages.add_message(request, messages.ERROR, 'An error has occurred, please try again later.')

    else:
        form = EditCategory(initial={'categories_text': category.categories_text})
    return render(request, 'edit_category.html', {'form': form})


@transaction.atomic
def delete_category(request):
    if request.method == 'POST' and request.is_ajax():
        categories_to_remove = Categories.objects.filter(id__in=[",".join(request.POST.getlist('ids[]'))])
        try:
            for category in categories_to_remove:
                Categories.objects.filter(id=category.id).delete()
        except Exception as e:
            messages.add_message(request, messages.ERROR, 'An error occurred, please try again later.')
    return HttpResponseRedirect(reverse('categories:categories_manager:manage_categories'))
