from django.db import models
from profile.models import Profile


class Notification(models.Model):
    # STATUS CHOICES
    READ = 'READ'
    NEW = 'NEW'

    STATUS_CHOICES = (
        (READ, 'READ'),
        (NEW, 'NEW')
    )

    # Notification types
    TRUST = 'TRUST'
    PAYMENT = 'PAYMENT'

    NOTIFICATION_TYPE_CHOICES = (
        (TRUST, 'TRUST'),
        (PAYMENT, 'PAYMENT')
    )

    notifier = models.ForeignKey(Profile, related_name='notifier')
    recipient = models.ForeignKey(Profile, related_name='notification_received')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)