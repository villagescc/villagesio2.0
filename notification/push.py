import requests
from notification.models import PushNotificationDevice
from django.conf import settings

title_dict = {
    "TRUST": "You were given trust. Trust them back?",
    "PAYMENT": "Received Village Hours Payment",
}
contents_dict = {
    "TRUST": "{notifier} trusted you with {amount} VH credit limit.\n{memo}",
    "PAYMENT": "{notifier} sent you {amount} VH for \n\"{memo}\"",
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
            "en": contents_dict[type].format(
                notifier=notifier,
                recipient=recipient,
                amount=kwargs.get("amount"),
                memo=kwargs.get("memo"),
            ),
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

    return True

