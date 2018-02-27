from django import template
from general.templatetags.image import resize
from django.conf import settings

register = template.Library()

# URL param key for username of link sharer.
SHARED_BY_USERNAME_KEY = 'u'

PROFILE_LINK_TEMPLATE = '''<a href="%s">%s</a>'''

@register.simple_tag
def profile_image_url(profile, size):
    if profile and profile.photo:
        return resize(profile.photo, size)
    else:
        square_side = min((int(i) for i in size.split('x')))
        return '/static/img/generic_user.png'


def profile_image_path_infinite_scroll(profile, size):
    if profile and profile.photo:
        return resize(profile.photo, size)
    else:
        square_side = min((int(i) for i in size.split('x')))
        return '/static/img/generic_user.png'

@register.simple_tag
def product_image_url(listing, size):
    if listing and listing.photo:
        return resize(listing.photo, size)
    else:
        square_side = min((int(i) for i in size.split('x')))
        return '/static/img/default_product.png'

@register.simple_tag
def profile_display(profile, request, text="you", not_you_text=None):
    if profile == request.profile:
        return text
    else:
        if not_you_text is not None:
            return not_you_text
        else:
            return PROFILE_LINK_TEMPLATE % (profile.get_absolute_url(), profile)

@register.inclusion_tag('share_link.html')
def share_link(profile):
    domain = settings.SITE_DOMAIN
    share_key = SHARED_BY_USERNAME_KEY    
    return locals()
