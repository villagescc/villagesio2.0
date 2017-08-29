from django.conf.urls import url, include
from management import views as management_views

urlpatterns = [
    url(r'^$', management_views.management, name='management'),
    url('^delete/?(.*)', management_views.delete_users, name='delete')
]