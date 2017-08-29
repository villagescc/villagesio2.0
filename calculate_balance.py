import os

os.environ["DJANGO_SETTINGS_MODULE"] = "ccproject.settings"

import django

django.setup()

from feed.models import FeedItem

feed_items = FeedItem.objects.filter(item_type='profile').all()

for each_item in feed_items:
    balance = each_item.poster.overall_balance()
    if balance:
        item_referral = FeedItem.objects.filter(poster=each_item.poster).update(balance=balance)