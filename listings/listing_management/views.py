from django.core.urlresolvers import reverse
from django.db import IntegrityError, transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib import messages

from listings.models import Listings
from listings.forms import ListingsForms
from tags.models import Tag


def view_listings(request):
    listing_form = ListingsForms()
    listings = Listings.objects.filter(user_id=request.user.id).all()
    return render(request, 'listing_management/manage_listings.html',
                  {'listings': listings, 'listing_form': listing_form})


def edit_listing(request, listing_id):
    listing = get_object_or_404(Listings, id=listing_id, user_id=request.user.id)
    if request.method == 'POST':
        form = ListingsForms(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            tags_list = form.cleaned_data.pop('tag').split(',')
            form.save()

            listing.tag.all().delete()
            if tags_list and tags_list[0] != u'':
                for tag in tags_list:
                    new_tag = Tag(name=tag)
                    try:
                        new_tag.save()
                        new_tag.listings_set.add(listing)
                    except IntegrityError as e:
                        existing_tag = Tag.objects.get(name=tag)
                        existing_tag.listings_set.add(listing)
            messages.success(request, 'Listing successfully edited.')
            return HttpResponseRedirect(reverse('my_profile'))
    else:
        tags_to_template = ''
        tags = listing.tag.all().values('name')
        if tags:
            for each_tag in tags:
                tags_to_template = tags_to_template + each_tag['name'].encode() + ','
        form = ListingsForms(instance=listing,
                             initial={'categories': listing.subcategories.categories if listing.subcategories else None,
                                      'tag': tags_to_template})
    return render(request, 'new_templates/add_post.html', {'form': form, 'listing_id': listing_id})


@transaction.atomic
def delete_listing(request, listing_id=''):
    if request.method == 'POST' and request.is_ajax():
        list_listings_to_remove = []
        for listing_id in request.POST.getlist('ids[]'):
            list_listings_to_remove.append(int(listing_id))
        listing_to_remove = Listings.objects.filter(id__in=list_listings_to_remove)
        try:
            for listings in listing_to_remove:
                Listings.objects.filter(id=listings.id).delete()
        except Exception as e:
            messages.add_message(request, messages.ERROR, 'An error occurred, please try again later.')
    elif listing_id:
        try:
            Listings.objects.filter(id=listing_id).delete()
            messages.add_message(request, messages.SUCCESS, 'Successfully deleted listing')
        except Exception as e:
            messages.add_message(request, messages.ERROR, 'Error deleting this listing')
    return HttpResponseRedirect(reverse('listing_management:manage_listings'))