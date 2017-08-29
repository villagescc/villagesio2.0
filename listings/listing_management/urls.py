from django.conf.urls import url, include
from listings.listing_management import views as listing_management_views

urlpatterns = [
    url(r'^$', listing_management_views.view_listings, name='manage_listings'),
    url('^edit/(.*)', listing_management_views.edit_listing, name='edit'),
    url('^delete/?(.*)', listing_management_views.delete_listing, name='delete')
]