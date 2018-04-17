from django.conf.urls import url, include
from listings.listing_management import views as listing_management_views

urlpatterns = [
    url(r'^$', listing_management_views.view_listings, name='manage_listings'),
    url('^(?P<listing_id>\d+)/edit/$', listing_management_views.edit_listing, name='edit'),
    url('^(?P<listing_id>\d+)/delete/$', listing_management_views.delete_listing, name='delete')
]