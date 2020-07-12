from django.conf.urls import url
from feed import views

urlpatterns = [
    url(r'^$', views.feed, {'do_filter': True}, name='feed'),
]
