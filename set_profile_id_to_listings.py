import os

os.environ["DJANGO_SETTINGS_MODULE"] = "ccproject.settings"

import django

django.setup()

from listings.models import Listings

all_listings = Listings.objects.all()

for each_listing in all_listings:
    each_listing.profile_id = each_listing.user.profile.id
    each_listing.save()
