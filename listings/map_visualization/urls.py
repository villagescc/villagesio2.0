from django.conf.urls import url

from listings.map_visualization.views import listing_map


urlpatterns = [
    url('^$', listing_map, name='map'),
]
