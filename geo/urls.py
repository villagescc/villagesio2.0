from django.conf.urls import url
from geo import views

urlpatterns = [
    url(r'^locator/$', views.locator, name='locator'),
]
