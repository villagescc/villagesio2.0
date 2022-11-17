from django.db import models

from account.models import AmountField
from profile.models import Profile


class Notification(models.Model):
    # STATUS CHOICES
    READ = 'READ'
    NEW = 'NEW'

    STATUS_CHOICES = (
        (READ, 'Read'),
        (NEW, 'New')
    )

    # Notification types
    TRUST = 'TRUST'
    PAYMENT = 'PAYMENT'

    NOTIFICATION_TYPE_CHOICES = (
        (TRUST, 'Trust'),
        (PAYMENT, 'Payment')
    )

    notifier = models.ForeignKey(Profile, related_name='notifier')
    recipient = models.ForeignKey(Profile, related_name='notification_received')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES)
    amount = AmountField(blank=True, null=True)
    memo = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=NEW)
    created_at = models.DateTimeField(auto_now_add=True)


class PushNotificationDevice(models.Model):
    """
    Class representing OneSignal info about device subscribed to push notifications
    """
    # PLATFORM CHOICES
    IOS = 0
    ANDROID = 1

    PLATFORM_CHOICES = (
        (IOS, 'iOS'),
        (ANDROID, 'Android')
    )
    profile = models.ForeignKey(Profile, related_name="device_profile", on_delete=models.CASCADE)
    device_id = models.CharField(max_length=60)
    push_token_identifier = models.CharField(max_length=120)
    device_type = models.IntegerField(max_length=2, choices=PLATFORM_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
