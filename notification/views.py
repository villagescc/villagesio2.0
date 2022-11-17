import json

from django.db.models.functions import Concat
from django.db.models import Value
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.http.response import HttpResponse
from django.http import Http404
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.conf import settings

from notification.models import Notification, PushNotificationDevice


@login_required()
def new_notifications(request):
    if request.is_ajax():
        new_notifications = Notification.objects.filter(recipient=request.profile, status=Notification.NEW)\
            .select_related('notifier__user').order_by('-created_at')[:5]

        parsed_new_notifications = render_to_string('new_templates/notifications_dropdown.html',
                                                    {'request': request, 'notifications': new_notifications})

        if new_notifications:
            Notification.objects.filter(recipient=request.profile, status=Notification.NEW)\
                .update(status=Notification.READ)
        return HttpResponse(parsed_new_notifications)
    else:
        raise Http404


@login_required()
def all_notifications(request):
    notifications = Notification.objects.filter(recipient=request.profile) \
        .annotate(notifier_name=Concat('notifier__name', Value(" ("), 'notifier__user__username', Value(")")))\
        .select_related('notifier__user').order_by('-created_at')
    page = request.GET.get('page', 1)

    paginator = Paginator(notifications, settings.NOTIFICATIONS_PER_PAGE)
    try:
        notifications = paginator.page(page)
    except PageNotAnInteger:
        notifications = paginator.page(1)
    except EmptyPage:
        notifications = paginator.page(paginator.num_pages)

    rendered_page = render(request, 'new_templates/notifications.html', {'notifications': notifications})
    Notification.objects.filter(recipient=request.profile, status=Notification.NEW).update(status=Notification.READ)
    return rendered_page


@login_required()
def subscribe_to_push(request):
    """
    Subscribe logged-in device to push notification
    """
    body = json.loads(request.body.decode('utf-8'))
    device = PushNotificationDevice(
        profile=request.profile,
        device_id=body.get("device_id"),
        push_token_identifier=body.get("push_token_identifier"),
        device_type=body.get("device_type")
    )
    device.save()
    return HttpResponse()


@login_required()
def unsubscribe_from_push(request):
    """
    Unsubscribe device when logged out
    """
    device = PushNotificationDevice.objects.filter(profile=request.profile)
    device.delete()
    return HttpResponse()
