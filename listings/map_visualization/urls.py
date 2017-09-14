from django.conf.urls import url

from listings.map_visualization.views import Search


urlpatterns = [
    url(r'^map/([^/]+)/$', Search.get, name='map_filter'),
    url('^$', Search.as_view(), name='map'),
]
