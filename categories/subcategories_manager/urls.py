from django.conf.urls import url, include
from categories.subcategories_manager import views as subcategories_views

urlpatterns = [
    url(r'^add/', subcategories_views.add_subcategory, name='add_subcategory'),
    url(r'^edit/(.*)', subcategories_views.edit_subcategory, name='edit_subcategory'),
    url(r'^delete/', subcategories_views.delete_subcategory, name='delete_subcategory'),
    url(r'^$', subcategories_views.view_subcategories, name='manage_subcategories')
]