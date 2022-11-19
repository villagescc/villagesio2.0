import requests
from notification.models import PushNotificationDevice
from django.conf import settings

title_dict = {
    "TRUST": "New Trust",
    "PAYMENT": "New Payment",
}
contents_dict = {
    "TRUST": "User {notifier} now trusts you, {recipient}",
    "PAYMENT": "User {notifier} have sent you a payment, {recipient}",
}

def send_push_notification(notifier, recipient, type, **kwargs):
    """
    Send push to profile's subscribed devices
    """
    devices = (
        PushNotificationDevice
        .objects
        .filter(profile__name=recipient)
        .all()
    )
    if not devices:
        return False

    url = "https://onesignal.com/api/v1/notifications"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = {
        "app_id": settings.ONE_SIGNAL_APP_ID,
        "include_player_ids": [str(device.device_id) for device in devices],
        "contents": {
            "en": kwargs.get("memo") or contents_dict[type].format(notifier=notifier, recipient=recipient),
        },
        "headings": {
            "en": title_dict[type],
        },
    }

    response = requests.post(
        url=url,
        headers=headers,
        json=payload,
        auth=("Basic", settings.ONE_SIGNAL_REST_API_KEY)
    ).json()

    if isinstance(response.get("errors"), dict):
        if response.get("errors").get("invalid_player_ids"):
            PushNotificationDevice.objects.filter(
                device_id__in=response.get("errors").get("invalid_player_ids")
            ).delete()

    # print response
    return True

