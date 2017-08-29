from .models import Notification


def create_notification(notifier, recipient, type):
    try:
        new_notification = Notification()
        new_notification.notifier = notifier
        new_notification.recipient = recipient
        new_notification.notification_type = type
        new_notification.status = Notification.NEW
        new_notification.save()
        return True
    except Exception as e:
        print(e)
        return False

