from django.conf.urls import url

from listings.map_visualization.views import Search


urlpatterns = [
    url('^$', Search.as_view(), name='map'),
]
