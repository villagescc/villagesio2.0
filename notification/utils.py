from .models import Notification, PushNotificationDevice
from profile.models import Profile

def create_notification(notifier, recipient, type, **kwargs):
    try:
        Notification.objects.create(
            notifier=notifier,
            recipient=recipient,
            notification_type=type,
            status=Notification.NEW,
            amount=kwargs.get('amount'),
            memo=kwargs.get('memo'),
        )
        return True
    except Exception as e:
        print(e)
        return False


def subscribe_to_push(user, device_id):
    """
    Subscribe logged-in device to push notification
    """
    if PushNotificationDevice.objects.get(device_id=device_id):
        return

    profile = Profile.objects.get(user__exact=user)
    device = PushNotificationDevice(
        profile=profile,
        device_id=device_id,
    )
    device.save()
