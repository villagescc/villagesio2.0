from django.conf.urls import url, include
import notification.views as notification_views

urlpatterns = [
    url(r'^new/', notification_views.new_notifications, name="notification"),
    url(r'^all/', notification_views.all_notifications, name="notification"),
]