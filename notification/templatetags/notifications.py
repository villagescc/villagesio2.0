from django import template

from notification.models import Notification

register = template.Library()


@register.assignment_tag(takes_context=True)
def new_notifications_count(context):
    request = context['request']
    notifications_count = Notification.objects.filter(status=Notification.NEW, recipient=request.profile).count()
    return notifications_count
