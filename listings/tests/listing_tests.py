import datetime
import unittest
import os
import django

os.environ["DJANGO_SETTINGS_MODULE"] = "ccproject.settings"
django.setup()

from django.db import IntegrityError
from profile.models import ProfilePageTag

from listings.models import Listings
from tags.models import Tag


def update_profile_tags(tag_obj, profile_id, listing_obj):
    existing_profile_tag = ProfilePageTag.objects.filter(tag_id=tag_obj.id, profile_id=929)
    if not existing_profile_tag:
        new_profile_page_tag = ProfilePageTag()
        new_profile_page_tag.tag_id = tag_obj.id
        new_profile_page_tag.listing_obj = listing_obj.id if listing_obj else None
        new_profile_page_tag.profile_id = profile_id
        new_profile_page_tag.listing_type = listing_obj.listing_type if listing_obj else None
        new_profile_page_tag.save()


class ListingTest(unittest.TestCase):
    def test_insert_listing_type_offer_success(self):
        new_listing = Listings()
        new_listing.title = 'OFFER Listing test'
        new_listing.price = 1
        new_listing.listing_type = 'OFFER'
        new_listing.user_id = 929
        new_listing.subcategories_id = 2
        new_listing.description = 'Listing Type Offer for testing'
        new_listing.created = datetime.datetime.now()
        new_listing.updated = datetime.datetime.now()
        new_listing.save()

        new_tag = Tag(name='offer_tag')
        try:
            new_tag.save()
            new_tag.listings_set.add(new_listing)
            update_profile_tags(new_tag, 929, new_listing)
        except IntegrityError:
            existing_tag = Tag.objects.get(name='offer_tag')
            existing_tag.listings_set.add(new_listing)
            update_profile_tags(existing_tag, 929, new_listing)

    def test_insert_listing_type_request_success(self):
        new_listing = Listings()
        new_listing.title = 'REQUEST Listing test'
        new_listing.price = 1
        new_listing.listing_type = 'REQUEST'
        new_listing.user_id = 929
        new_listing.subcategories_id = 2
        new_listing.description = 'Listing Type Request for testing'
        new_listing.created = datetime.datetime.now()
        new_listing.updated = datetime.datetime.now()
        new_listing.save()

        new_tag = Tag(name='request_tag')
        try:
            new_tag.save()
            new_tag.listings_set.add(new_listing)
            update_profile_tags(new_tag, 929, new_listing)
        except IntegrityError:
            existing_tag = Tag.objects.get(name='offer_tag')
            existing_tag.listings_set.add(new_listing)
            update_profile_tags(existing_tag, 929, new_listing)

    def test_insert_listing_type_learn_success(self):
        new_listing = Listings()
        new_listing.title = 'LEARN Listing test'
        new_listing.price = 1
        new_listing.listing_type = 'LEARN'
        new_listing.user_id = 929
        new_listing.subcategories_id = 2
        new_listing.description = 'Listing Type Learn for testing'
        new_listing.created = datetime.datetime.now()
        new_listing.updated = datetime.datetime.now()
        new_listing.save()

        new_tag = Tag(name='learn_tag')
        try:
            new_tag.save()
            new_tag.listings_set.add(new_listing)
            update_profile_tags(new_tag, 929, new_listing)
        except IntegrityError:
            existing_tag = Tag.objects.get(name='offer_tag')
            existing_tag.listings_set.add(new_listing)
            update_profile_tags(existing_tag, 929, new_listing)

    def test_insert_listing_type_teach_success(self):
        new_listing = Listings()
        new_listing.title = 'TEACH Listing test'
        new_listing.price = 1
        new_listing.listing_type = 'TEACH'
        new_listing.user_id = 929
        new_listing.subcategories_id = 2
        new_listing.description = 'Listing Type Teach for testing'
        new_listing.created = datetime.datetime.now()
        new_listing.updated = datetime.datetime.now()
        new_listing.save()

        new_tag = Tag(name='teach_tag')
        try:
            new_tag.save()
            new_tag.listings_set.add(new_listing)
            update_profile_tags(new_tag, 929, new_listing)
        except IntegrityError:
            existing_tag = Tag.objects.get(name='offer_tag')
            existing_tag.listings_set.add(new_listing)
            update_profile_tags(existing_tag, 929, new_listing)