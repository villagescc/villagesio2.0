from django.conf import settings
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.contrib.gis.db.models import GeoManager, Q

from decimal import Decimal

from categories.models import Categories, SubCategories
from tags.models import Tag
from profile.models import Profile
from general.util import reverse_querystring


OFFER = 'OFFER'
REQUEST = 'REQUEST'
TEACH = 'TEACH'
LEARN = 'LEARN'
# GIFT = 'GIFT'

LISTING_TYPE = (
    ('OFFER', OFFER),
    ('REQUEST', REQUEST),
    ('TEACH', TEACH),
    ('LEARN', LEARN),
    # ('GIFT', GIFT),
)

LISTING_TYPE_CHECK = ['OFFER', 'REQUEST', 'TEACH', 'LEARN']

TRUSTED_SUBQUERY = (
    "feed_feeditem.poster_id in "
    "(select to_profile_id from profile_profile_trusted_profiles "
    "    where from_profile_id = %s)")


class ListingsManager(GeoManager):
    def get_items_and_remaining(self, *args, **kwargs):
        count_kwargs = kwargs.copy()
        count_kwargs.pop('start_limit', None)
        count_kwargs.pop('end_limit', None)

        count = self.get_items_count(self, *args, **count_kwargs)
        if count > 0:
            items = self.get_items(*args, **kwargs)
        else:
            items = []
        return items, count - len(items)

    def get_items_count(self, *args, **kwargs):
        return self._item_query(*args, **kwargs).count()

    def get_items(self, *args, **kwargs):
        start_limit = kwargs.pop('start_limit', 0)
        end_limit = kwargs.pop('end_limit', settings.LISTING_ITEMS_PER_PAGE)
        items = self._item_query(*args, **kwargs)[start_limit:end_limit]
        return items

    def _item_query(self, profile=None, location=None, radius=None, tsearch=None, trusted_only=False,
                    up_to_date=None, request_profile=None, type_filter=None, listing_type=None):
        query = self.get_queryset().order_by('-updated')
        if trusted_only and request_profile:
            profile_obj_list = []
            trusting_profiles = request_profile.trusted_profiles.through.objects.filter(from_profile_id=request_profile.id)
            for each_trusting in trusting_profiles:
                profile_obj_list.append(each_trusting.to_profile)
            query = query.filter(profile_id__in=profile_obj_list)
        if up_to_date:
            query = query.filter(updated__lt=up_to_date)
        if location and radius:
            query = query.filter(user__profile__location__point__dwithin=(location.point, radius))

        if tsearch:
            # Searching by TAGs
            query = query.filter(Q(title__icontains=tsearch) |
                                 Q(description__icontains=tsearch) |
                                 Q(tag__name=tsearch)).distinct()

        if type_filter:
            if type_filter in LISTING_TYPE_CHECK:
                query = query.filter(listing_type=type_filter).order_by('-updated')
            elif Categories.objects.filter(categories_text=type_filter):
                query = query.filter(subcategories__categories__categories_text=type_filter).order_by('-updated')
            else:
                query = query.filter(subcategories__id=type_filter).order_by('-updated')

        if listing_type:
            query = query.filter(listing_type=listing_type).order_by('-updated')

        return query


@python_2_unicode_compatible
class Listings(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    profile = models.ForeignKey(Profile, null=True, blank=True)
    title = models.CharField(max_length=70)
    description = models.CharField(max_length=5000, null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0'))
    subcategories = models.ForeignKey(SubCategories, null=True, blank=True)
    # tag = models.ForeignKey(TagListing, null=True, blank=True)

    listing_type = models.CharField(max_length=100, choices=LISTING_TYPE)
    photo = models.ImageField(upload_to='listings', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    tag = models.ManyToManyField(Tag, blank=True)

    objects = ListingsManager()

    @property
    def date(self):
        return self.updated

    def get_trust_link(self):
        return reverse_querystring('blank_trust_user', query_kwargs={'recipient_name': self.user.username})

    def get_payment_link(self):
        return reverse_querystring('blank_payment_user', query_kwargs={'recipient_name': self.user.username,
                                                                       'amount': self.price,
                                                                       'memo': self.title})

    def get_contact_link(self):
        return reverse_querystring('undefined_contact', query_kwargs={'recipient_name': self.user.username,
                                                                      'listing_id': self.id})

    def __str__(self):
        return self.title
