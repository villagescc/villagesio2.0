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


class Search(View):
    def get(self, request):
        form = ListingsForms()
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

        return render(request, 'frontend/plugs/map-visualization.html',
                      {'listing_form': form, 'categories': categories_list, 'item_sub_categories': item_sub_categories,
                       'services_sub_categories': services_sub_categories, 'subcategories': subcategories,
                       'rideshare_sub_categories': rideshare_sub_categories,
                       'housing_sub_categories': housing_sub_categories,
                       'payment_form': payment_form, 'contact_form': contact_form,
                       'notification_number': notification_number})

    def post(self, request):

        listing_locations = []

        all_listings = Listings.objects.all()
        post_data = json.loads(request.body.decode('utf-8'))
        for listing_location in all_listings:
            listing_locations.append({'lat': listing_location.user.profile.location.point.coords[1],
                                      'lng': listing_location.user.profile.location.point.coords[0],
                                      'seller': listing_location.user.profile.name,
                                      'price': listing_location.price,
                                      'title': listing_location.title})

        return JsonResponse({'listing_locations': listing_locations})