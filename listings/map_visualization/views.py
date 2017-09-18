import json
from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from listings.models import Listings
from listings.forms import ListingsForms
from categories.models import Categories, SubCategories
from notification.models import Notification
from profile.forms import ContactForm
from relate.forms import AcknowledgementForm


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

        categories_list = Categories.objects.all()
        item_sub_categories = SubCategories.objects.all().filter(categories=1)
        services_sub_categories = SubCategories.objects.all().filter(categories=2)
        rideshare_sub_categories = SubCategories.objects.all().filter(categories=3)
        housing_sub_categories = SubCategories.objects.all().filter(categories=4)
        payment_form = AcknowledgementForm(max_ripple=None, initial=request.GET)
        categories_list = Categories.objects.all()
        subcategories = SubCategories.objects.all()
        contact_form = ContactForm()

        notification_number = Notification.objects.filter(status='NEW', recipient=request.profile).count()

        if request.GET.get('map_price'):

            min_price = request.GET.get('map-price').split(',')[0]
            max_price = request.GET.get('map-price').split(',')[1]

            query = Listings.objects.filter(price__range=(min_price,
                                                          max_price))

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

        return render(request, 'frontend/plugs/map-visualization.html',
                      {'listing_form': form, 'categories': categories_list, 'item_sub_categories': item_sub_categories,
                       'services_sub_categories': services_sub_categories, 'subcategories': subcategories,
                       'rideshare_sub_categories': rideshare_sub_categories,
                       'housing_sub_categories': housing_sub_categories,
                       'payment_form': payment_form, 'contact_form': contact_form,
                       'notification_number': notification_number, 'listing_locations': listing_locations})