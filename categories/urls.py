from django.conf.urls import url, include

urlpatterns = [
    url(r'', include('categories.categories_manager.urls', namespace='categories_manager')),
    url(r'^subcategories/', include('categories.subcategories_manager.urls', namespace='subcategories_manager')),
]