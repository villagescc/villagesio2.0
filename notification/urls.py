from django.conf.urls import url, include
import notification.views as notification_views

urlpatterns = [
    url(r'^notifications/', notification_views.notification, name="notification"),
]