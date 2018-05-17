from django.core.urlresolvers import reverse
from django.db import IntegrityError, transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django_user_agents.utils import get_user_agent

from listings.models import Listings
from listings.forms import ListingsForms
from tags.models import Tag


def view_listings(request):
    listing_form = ListingsForms()
    listings = Listings.objects.filter(user_id=request.user.id).all()
    return render(request, 'listing_management/manage_listings.html',
                  {'listings': listings, 'listing_form': listing_form})


@login_required
def edit_listing(request, listing_id):
    listing = get_object_or_404(Listings, id=listing_id, user_id=request.user.id)
    if request.method == 'POST':
        user_agent = get_user_agent(request)
        form = ListingsForms(request.POST, request.FILES, user_agent=user_agent, instance=listing)
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
    return render(request, 'new_templates/post_edit.html', {'form': form, 'listing_id': listing_id})


@transaction.atomic
@login_required
def delete_listing(request, listing_id):
    listing = get_object_or_404(Listings, id=listing_id, user_id=request.user.id)
    if request.method == 'POST':
        if "cancel" in request.POST:
            messages.info(request, 'Deletion canceled.')
        else:
            try:
                listing.delete()
            except Exception as e:
                messages.error(request, 'A server error occurred, please try again later.')
            else:
                messages.success(request, 'Successfully deleted post.')
        return HttpResponseRedirect(reverse('my_profile'))

    else:
        return render(request, 'new_templates/delete_form.html', {'listing': listing, 'profile': request.user.profile})
