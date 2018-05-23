from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.gis.geos import Point
from django.conf import settings

from .models import Location

import requests


def location_required(view_func):
    """
    View decorator that requires request.location to be set.
    If no session location yet, get default from request.user,
    or else redirect to locator view.
    """

    # TODO: Don't just redirect to locator view when there's no
    # location, autodetect from IP and browser and set session location
    # in cookie.  Use default names from geocoding.
    # Have separate decorator home_location_required for when we
    # need the name of the location?

    def decorated_func(request, *args, **kwargs):
        if not request.location:
            return HttpResponseRedirect("%s?%s=%s" % (
                    reverse('locator'), REDIRECT_FIELD_NAME, request.path))
        return view_func(request, *args, **kwargs)
    return decorated_func


def build_location(loc):
    location = None
    loc_encode = unicode(loc).encode('utf-8')
    URL = 'https://maps.googleapis.com/maps/api/geocode/json?' \
          'address={}&key={}'.format(loc_encode,
                                     settings.GOOGLE_MAPS_API_KEY)
    r = requests.get(URL)
    res_json = r.json()
    if res_json['status'] == 'OK':
        lat = res_json['results'][0]['geometry']['location']['lat']
        lng = res_json['results'][0]['geometry']['location']['lng']
        address_components = res_json['results'][0]['address_components']
        city = ''
        state = ''
        country = ''
        for item in address_components:
            if item['types'][0] == 'locality':
                city = item['long_name']
            if item['types'][0] == 'administrative_area_level_1':
                state = item['long_name']
            if item['types'][0] == 'country':
                country = item['long_name']

        location = Location(point=Point(lng, lat),
                            country=country,
                            state=state,
                            city=city)
        location.save()
    return location
