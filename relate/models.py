from django.db.models.signals import post_save, post_delete
from django.db import models, connection, transaction
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

from profile.models import Profile
import ripple.api as ripple


class EndorsementManager(models.Manager):
    def rebuild_trust_network(self):
        "Clear out all Profile.trusted_profiles and recreate from scratch."
        with transaction.atomic():
            cursor = connection.cursor()
            cursor.execute("delete from profile_profile_trusted_profiles")
            for endorsement in self.all():
                endorsement.update_trust_network()


class Endorsement(models.Model):
    endorser = models.ForeignKey(Profile, related_name='endorsements_made', on_delete=models.CASCADE)
    recipient = models.ForeignKey(
        Profile, related_name='endorsements_received', on_delete=models.CASCADE)
    weight = models.PositiveIntegerField(_("Weight"), help_text=_(
            "Each heart represents an hour of value you'd provide "
            "in exchange for acknowledgements."))
    text = models.TextField(_("Testimonial"), blank=True)
    updated = models.DateTimeField(auto_now=True)

    objects = EndorsementManager()

    class Meta:
        unique_together = ('endorser', 'recipient')

    FEED_TEMPLATE = 'endorsement_feed_item.html'

    def __unicode__(self):
        return u'%s endorses %s (%d)' % (
            self.endorser, self.recipient, self.weight)

    def get_absolute_url(self):
        return reverse('endorsement', args=[self.id,])

    @property
    def date(self):
        """
        For FeedItem source interface, returns last updated date as the
        feed item date.
        """
        return self.updated

    @property
    def location(self):
        "For FeedItem source interface.  Endorsements have no location."
        return None

    @property
    def feed_public(self):
        return False

    @property
    def feed_recipient(self):
        return self.recipient

    @property
    def feed_poster(self):
        return self.endorser

    def get_search_text(self):
        return [(self.text, 'B'),
                (self.endorser.name, 'C'),
                (self.endorser.username, 'C'),
                (self.recipient.name, 'C'),
                (self.recipient.username, 'C'),
               ]

    def can_edit(self, profile):
        return self.endorser == profile

    def update_trust_network(self):
        """
        Add endorsement recipient plus recipient's entire trust network to
        the trusted network of endorser and everyone who trusts endorser.
        """
        to_trust = set(self.recipient.trusted_profiles.only('id'))
        to_trust.add(self.recipient)
        to_trust = tuple(to_trust)
        trusters = set(self.endorser.trusting_profiles.only('id'))
        trusters.add(self.endorser)
        for truster in trusters:
            truster.trusted_profiles.add(*to_trust)

    @classmethod
    def get_by_id(cls, id):
        return cls.objects.get(pk=id)

    @classmethod
    def post_save(cls, sender, instance, created, **kwargs):
        ripple.update_credit_limit(instance)
        if created:
            instance.update_trust_network()

    @classmethod
    def post_delete(cls, sender, instance, **kwargs):
        ripple.update_credit_limit(instance)
        # TODO: Do something more efficient than rebuild trust network
        # from scratch here.
        cls.objects.rebuild_trust_network()

post_save.connect(Endorsement.post_save, sender=Endorsement,
                  dispatch_uid='relate.models')
# post_delete.connect(Endorsement.post_delete, sender=Endorsement,
#                     dispatch_uid='relate.models')


class Referral(models.Model):
    referrer = models.ForeignKey(Profile, related_name='referral_made', on_delete=models.CASCADE)
    recipient = models.ForeignKey(
        Profile, related_name='referral_received', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)

    @property
    def date(self):
        """
        For FeedItem source interface, returns last updated date as the
        feed item date.
        """
        return self.created_at

    @classmethod
    def get_by_id(cls, id):
        return cls.objects.get(pk=id)

    @property
    def location(self):
        "For FeedItem source interface.  Endorsements have no location."
        return None

    @property
    def feed_public(self):
        return False

    @property
    def feed_recipient(self):
        return self.recipient

    @property
    def feed_poster(self):
        return self.referrer

    def get_search_text(self):
        return [(self.referrer.name, 'C'),
                (self.referrer.username, 'C'),
                (self.recipient.name, 'C'),
                (self.recipient.username, 'C'),
               ]