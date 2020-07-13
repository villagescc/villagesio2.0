from django.conf.urls import url, include

urlpatterns = [
    url(r'', include(('categories.categories_manager.urls', 'categories.categories_manager'), namespace='categories_manager')),
    url(r'^subcategories/', include(('categories.subcategories_manager.urls', 'categories.subcategories_manager'), namespace='subcategories_manager')),
]