from django.conf.urls import url, include
from categories.categories_manager import views as categories_views

urlpatterns = [
    url(r'^add/', categories_views.add_category, name='add_category'),
    url(r'^edit/(.*)', categories_views.edit_category, name='edit_category'),
    url(r'^delete/', categories_views.delete_category, name='delete_category'),
    url(r'^$', categories_views.view_categories, name='manage_categories')
]