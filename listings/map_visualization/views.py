import json
from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse

from feed.models import FeedItem
from listings.models import Listings
from listings.forms import ListingsForms
from categories.models import Categories, SubCategories
from notification.models import Notification
from profile.forms import ContactForm
from relate.forms import AcknowledgementForm

TRUSTED_SUBQUERY = (
    "feed_feeditem.poster_id in "
    "(select to_profile_id from profile_profile_trusted_profiles "
    "    where from_profile_id = %s)")


def listing_map(request):
    if request.method == 'POST':
        listing_locations = []

        post_data = json.loads(request.body.decode('utf-8'))

        if post_data.get('max_price'):
            query = Listings.objects.filter(price__range=(post_data['min_price'],
                                                          post_data['max_price']))

            for each_listing in query:
                listing_locations.append({'lat': each_listing.user.profile.location.point.coords[1],
                                          'lng': each_listing.user.profile.location.point.coords[0],
                                          'seller': each_listing.user.profile.name,
                                          'seller_username': each_listing.user.username,
                                          'listing_id': each_listing.id,
                                          'price': each_listing.price,
                                          'title': each_listing.title,
                                          'listing_img': each_listing.photo.url if each_listing.photo else None,
                                          'profile_img': each_listing.user.profile.photo.url if each_listing.user.profile.photo else None})
            return JsonResponse({'listing_locations': listing_locations})

        all_listings = Listings.objects.all()
        for listing_location in all_listings:
            listing_locations.append({'lat': listing_location.user.profile.location.point.coords[1],
                                      'lng': listing_location.user.profile.location.point.coords[0],
                                      'seller': listing_location.user.profile.name,
                                      'seller_username': listing_location.user.username,
                                      'listing_id': listing_location.id,
                                      'price': listing_location.price,
                                      'title': listing_location.title,
                                      'listing_img': listing_location.photo.url if listing_location.photo else None,
                                      'profile_img': listing_location.user.profile.photo.url if listing_location.user.profile.photo else None})
        return JsonResponse({'listing_locations': listing_locations})

    else:
        form = ListingsForms()
        listing_locations = []

        item_sub_categories = SubCategories.objects.all().filter(categories=1)
        services_sub_categories = SubCategories.objects.all().filter(categories=2)
        rideshare_sub_categories = SubCategories.objects.all().filter(categories=3)
        housing_sub_categories = SubCategories.objects.all().filter(categories=4)
        payment_form = AcknowledgementForm(max_ripple=None, initial=request.GET)
        categories_list = Categories.objects.all()
        subcategories = SubCategories.objects.all()
        contact_form = ContactForm()

        if request.GET.get('map-price'):
            min_price = request.GET.get('map-price').split(',')[0]
            max_price = request.GET.get('map-price').split(',')[1]
        else:
            min_price = 0
            max_price = 1000

        query = Listings.objects.filter(price__range=(min_price,
                                                      max_price))

        if request.GET.get('trusted'):
            profile_obj_list = []
            trusting_profiles = request.profile.trusted_profiles.through.objects.filter(
                from_profile_id=request.profile.id)

            if trusting_profiles:
                for each_trusting in trusting_profiles:
                    profile_obj_list.append(each_trusting.to_profile)
                query = query.filter(profile_id__in=profile_obj_list)

        if request.GET.get('listing_type'):
            query = query.filter(listing_type=request.GET.get('listing_type').upper())

        if request.GET.get('category'):
            query = query.filter(subcategories__categories__id=int(request.GET.get('category')))

        if request.GET.get('subcategory'):
            query = query.filter(subcategories_id=request.GET.get('subcategory'))

        if request.GET.get('balance_type'):
            balance_type_list = []
            if request.GET.get('balance_type') == 'positive':
                positive_balances = FeedItem.objects.filter(balance__gte=0).all()
                for each_positive in positive_balances:
                    balance_type_list.append(each_positive.poster)
                query = query.filter(profile_id__in=balance_type_list)
            elif request.GET.get('balance_type') == 'negative':
                negative_balances = FeedItem.objects.filter(balance__lt=0).all()
                for each_negative in negative_balances:
                    balance_type_list.append(each_negative.poster)
                query = query.filter(profile_id__in=balance_type_list)

        for each_listing in query:
            try:
                if each_listing.user.profile.location:
                    listing_locations.append({'lat': each_listing.user.profile.location.point.coords[1],
                                              'lng': each_listing.user.profile.location.point.coords[0],
                                              'seller': each_listing.user.profile.name,
                                              'seller_username': each_listing.user.username,
                                              'listing_id': each_listing.id,
                                              'price': int(each_listing.price),
                                              'title': each_listing.title,
                                              'listing_img': each_listing.photo.url if each_listing.photo else None,
                                              'profile_img': each_listing.user.profile.photo.url if each_listing.user.profile.photo else None})
            except Exception as e:
                print(e)

        listing_locations = json.dumps(listing_locations)

        return render(request, 'new_templates/map-visualization.html',
                      {'listing_form': form, 'categories': categories_list, 'item_sub_categories': item_sub_categories,
                       'services_sub_categories': services_sub_categories, 'subcategories': subcategories,
                       'rideshare_sub_categories': rideshare_sub_categories,
                       'housing_sub_categories': housing_sub_categories,
                       'payment_form': payment_form, 'contact_form': contact_form,
                       'listing_locations': listing_locations, 'min_price': min_price, 'max_price': max_price})
