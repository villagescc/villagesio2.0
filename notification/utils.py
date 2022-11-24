from .models import Notification


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

