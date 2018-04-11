from django.db.models.functions import Concat
from django.db.models import Value
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.http.response import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.conf import settings

from notification.models import Notification


@login_required()
def new_notifications(request):
    notifications = Notification.objects.filter(recipient=request.profile, status=Notification.NEW)\
        .select_related('notifier__user')\
        .annotate(notifier_name=Concat('notifier__name', Value(" ("), 'notifier__user__username', Value(")")))\
        .order_by('-created_at')[:5]

    parsed_notifications = render_to_string('new_templates/notifications_dropdown.html',
                                            {'request': request, 'notifications': notifications})

    Notification.objects.filter(recipient=request.profile, status=Notification.NEW).update(status=Notification.READ)
    return HttpResponse(parsed_notifications)


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

    Notification.objects.filter(recipient=request.profile, status=Notification.NEW).update(status=Notification.READ)
    return render(request, 'new_templates/notifications.html', {'notifications': notifications})
