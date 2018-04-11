from django.db.models.functions import Concat
from django.db.models import Value
from django.shortcuts import render
from django.http.response import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required

from notification.models import Notification


@login_required()
def new_notifications(request):
    new_notifications = Notification.objects.filter(recipient=request.profile, status=Notification.NEW)\
        .select_related('notifier__user')\
        .annotate(notifier_name=Concat('notifier__name', Value(" ("), 'notifier__user__username', Value(")")))\
        .order_by('-created_at')

    parsed_notifications = ''
    for notification in new_notifications:
        parsed_notifications += render_to_string('new_templates/notifications_new_item.html',
                                                 {'request': request, 'notification': notification})

    notifications.update(status=Notification.READ)
    return HttpResponse(parsed_notifications)


@login_required()
def all_notifications(request):
    notifications = Notification.objects.filter(recipient=request.profile)\
        .select_related('notifier__user').order_by('-created_at')

    notifications.update(status=Notification.READ)
    return render(request, 'new_templates/notifications.html', {'notifications': notifications})
