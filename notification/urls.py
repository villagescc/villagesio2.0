from django.conf.urls import url

import notification.views as notification_views

urlpatterns = [
    url(r'^new/', notification_views.new_notifications, name="new_notifications"),
    url(r'^all/', notification_views.all_notifications, name="all_notifications"),
]