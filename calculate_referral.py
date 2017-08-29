import os
import elasticsearch

os.environ["DJANGO_SETTINGS_MODULE"] = "ccproject.settings"

import django

django.setup()

from feed.models import FeedItem

feed_items = FeedItem.objects.filter(item_type='profile').all()

for each_item in feed_items:
    referral_count = each_item.poster.referral_received.count()
    if referral_count:
        item_referral = FeedItem.objects.filter(poster=each_item.poster).update(referral_count=referral_count)