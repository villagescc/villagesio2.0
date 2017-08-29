from django.conf.urls import url
from about import views as about_views

urlpatterns = [
    url(r'^how_it_works/', about_views.how_it_works, name='how_it_works'),
    url(r'^motivation/', about_views.motivation, name='motivation'),
    url(r'^privacy/', about_views.privacy, name='privacy'),
    url(r'^developers/', about_views.developers, name='developers'),
    url(r'^donate/', about_views.donate, name='donate'),
    url(r'^contact/', about_views.contact_us, name='contact_us'),
]