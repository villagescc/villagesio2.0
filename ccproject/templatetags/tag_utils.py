from django import template
from relate.models import Referral

register = template.Library()


@register.filter(name='check_is_trusted')
def is_trusted(profile, recipient):
    return profile.profile.trusts(recipient.user.profile)


@register.filter(name='check_is_trusted_listing')
def is_trusted_listing(listing, profile):
    return listing.user.profile.trusts(profile)


@register.filter(name='check_referral')
def is_referred(referrer, recipient):
    return True if Referral.objects.filter(referrer=referrer, recipient=recipient) else False
