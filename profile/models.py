from datetime import datetime
import random

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save, pre_save, post_delete
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.dispatch import receiver
from django.contrib.gis.db.models import GeoManager
from django.db.models import Q
from general.models import VarCharField, EmailField
from geo.models import Location
import ripple.api as ripple
from general.util import cache_on_object
from general.mail import send_mail, email_str, send_mail_from_system
from django.utils import translation
from django.utils.translation import get_language_info as lang_info
from django.utils.translation import ugettext_lazy as _
from tags.models import Tag

CODE_LENGTH = 20
CODE_CHARS = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

TRUSTED_SUBQUERY = (
    "feed_feeditem.poster_id in "
    "(select to_profile_id from profile_profile_trusted_profiles "
    "    where from_profile_id = %s)")


class QueryManager(GeoManager):

    def _trusted_profiles_query(self, profile=None, location=None, radius=None, tsearch=None, trusted_only=None,
                                up_to_date=None):
        query = self.get_queryset().order_by('-date')
        if up_to_date:
            query = query.filter(date__lt=up_to_date)
        if profile:
            query = query.extra(
                select={'trusted': TRUSTED_SUBQUERY},
                select_params=[profile.id])
        if trusted_only and profile:
            query = query.extra(where=[TRUSTED_SUBQUERY], params=[profile.id])
        if location and radius:
            query = query.filter(
                # TODO: Bounding box query might be faster?
                Q(location__point__dwithin=(location.point, radius)) |
                Q(location__isnull=True))
        if tsearch:
            query = query.extra(
                where=["tsearch @@ plainto_tsquery(%s)"],
                params=[tsearch])
        return query


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    name = VarCharField(_("Name"), blank=True)
    location = models.ForeignKey(Location, null=True, blank=True)
    photo = models.ImageField(_("Photo"),
                              upload_to='user/%Y/%m', max_length=256, blank=True)
    header_image = models.ImageField(_("Header Image"),
                              upload_to='user/%Y/%m', max_length=256, blank=True)
    description = models.TextField(_("Description"), blank=True)

    job = models.TextField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    trusted_profiles = models.ManyToManyField(
        'Profile', symmetrical=False, related_name='trusting_profiles',
        blank=True)

    # TODO: Should a profile always trust itself?

    FEED_TEMPLATE = 'profile_feed_item.html'
    
    def __unicode__(self):
        return self.name or self.username

    @models.permalink
    def get_absolute_url(self):
        return 'profile', (self.username,)

    def set_updated(self):
        """
        Call this every time a user-facing change is made to profile that
        should cause it to be bumped to the top of the feed.
        Must still save the profile after to have any effect.
        """
        self.updated = datetime.now()

    @property
    def username(self):
        # Username is stored in django User model.
        return self.user.username

    @property
    def email(self):
        return self.settings.email

    @property
    def endorsement_limited(self):
        return self.settings.endorsement_limited
    
    def endorsement_for(self, recipient):
        "Returns this profile's endorsement of recipient, or None."
        try:
            return self.endorsements_made.get(recipient=recipient)
        except ObjectDoesNotExist:
            return None

    @property
    def date(self):
        return self.updated

    # TODO: Consider putting profile at top of feed whenever they come
    # back online?
    
    @property
    def text(self):
        return self.description
    
    @property
    def feed_public(self):
        return True

    @property
    def feed_recipient(self):
        return None

    @property
    def feed_poster(self):
        return self

    def get_search_text(self):
        return [(self.name, 'A'),
                (self.username, 'A'),
                (self.description, 'B'),
               ]

    @property
    @cache_on_object
    def endorsement_count(self):
        return self.endorsements_received.all().count()
    
    @property
    @cache_on_object
    def endorsement_sum(self):
        return self.endorsements_received.all().aggregate(
            models.Sum('weight')).get('weight__sum') or 0

    @property
    @cache_on_object
    def endorsements_made_sum(self):
        return (
            (self.endorsements_made.all().aggregate(
                models.Sum('weight')).get('weight__sum') or 0) +
            (self.invitations_sent.all().aggregate(
                models.Sum('endorsement_weight')).get(
                'endorsement_weight__sum') or 0))

    @property
    @cache_on_object
    def endorsements_remaining(self):
        return max(((self.endorsement_count + 1) * settings.ENDORSEMENT_BONUS -
                    self.endorsements_made_sum), 0)

    @property
    def can_endorse(self):
        return not self.endorsement_limited or self.endorsements_remaining > 0
    
    def reputation(self, asker):
        """"
        Returns max flow of endorsements from asker to self across endorsement
        network.
        """
        return ripple.credit_reputation(self, asker)

    def overall_balance(self):
        return ripple.overall_balance(self)

    def trusted_balance(self):
        "Overall balance minus acknowledgements received beyond trusted limits."
        return ripple.trusted_balance(self)

    def trusts(self, profile):
        return self.trusted_profiles.filter(pk=profile.id).count() > 0

    def account(self, profile):
        return ripple.get_account(self, profile)

    def email_str(self):
        """
        Returns '"Name" <email>' suitable for email headers.
        """
        return email_str(self.name, self.email)
    
    @classmethod
    def get_by_id(cls, id):
        return cls.objects.get(pk=id)

    @classmethod
    def post_save(cls, sender, instance, created, **kwargs):
        # Create Settings for this profile if it is new.
        if created:
            Settings.objects.create(profile=instance)

    @classmethod
    def post_delete(cls, sender, instance, **kwargs):
        # Delete related records in Ripple backend.
        ripple.delete_node(instance)

post_save.connect(Profile.post_save, sender=Profile,
                  dispatch_uid='profile.models')

post_delete.connect(Profile.post_delete, sender=Profile,
                    dispatch_uid='profile.models')


class Settings(models.Model):
    "Profile settings."
    profile = models.OneToOneField(Profile, related_name='settings', on_delete=models.CASCADE)
    email = EmailField(blank=True)
    endorsement_limited = models.BooleanField(
        _("Limited hearts"), default=True, help_text=_(
            "Uncheck this if you know what you're doing and want to give "
            "out more hearts."))
    send_notifications = models.BooleanField(
        _("Receive notifications"), default=True, help_text=_(
            "Receive email whenever someone endorses or acknowledges you."))
    send_newsletter = models.BooleanField(
        _("Receive updates"), default=True, help_text=_(
            "Receive occasional news about the Villages community."))
    langs = [(l[0], lang_info(l[0])['name_local']) for l in settings.LANGUAGES]
    language = VarCharField(
        _("Language"), default="en", max_length=8, choices=langs)
    # Sticky form settings.
    feed_radius = models.IntegerField(null=True, blank=True)
    feed_trusted = models.BooleanField(default=False)

    def __unicode__(self):
        return _(u"Settings for %s") % self.profile


class Invitation(models.Model):
    from_profile = models.ForeignKey(Profile, related_name='invitations_sent')
    to_email = EmailField(_("Friend's email"))
    endorsement_weight = models.PositiveIntegerField(_("Hearts"), help_text=_(
            "Each heart represents an hour of value you'd provide "
            "in exchange for acknowledgements."))
    endorsement_text = models.TextField(_("Testimonial"), blank=True)
    message = models.TextField(
        _("Private message"), blank=True,
        help_text=_("Sent with the invitation email only. Not public."))
    
    date = models.DateTimeField(auto_now_add=True)
    code = VarCharField(unique=True)

    # TODO: Some help text in fields above.

    # TODO: Cron job to delete old invitations?

    def __unicode__(self):
        return u"%s invites %s" % (self.from_profile, self.to_email)

    @models.permalink
    def get_absolute_url(self):
        return 'invitation', (self.code,)

    def send(self):
        send_mail(_("%s Has Invited You To Villages.io") % self.from_profile,
                  self.from_profile, self.to_email, 'invitation_email.txt',
                  {'invitation': self})
        self.date = datetime.now()
        self.save()
        
    @classmethod
    def pre_save(cls, sender, instance, **kwargs):
        if not instance.code:
            instance.code = generate_code()

# Fill in code before saving.
pre_save.connect(Invitation.pre_save, sender=Invitation,
                 dispatch_uid='profile.models')


class PasswordResetLink(models.Model):
    profile = models.ForeignKey(Profile)
    code = VarCharField(unique=True)
    expires = models.DateTimeField()

    def __unicode__(self):
        return _("Password reset link for %s") % self.profile

    @models.permalink
    def get_absolute_url(self):
        return 'reset_password', (self.code,)

    def send(self):
        subject = _("Villages.io Password Reset Link")
        send_mail_from_system(subject, self.profile, 'password_reset_email.txt',
                              {'link': self})

    @classmethod
    def pre_save(cls, sender, instance, **kwargs):
        if not instance.code:
            instance.code = generate_code()
        if not instance.expires:
            instance.expires = (
                datetime.now() + settings.PASSWORD_RESET_LINK_EXPIRY)

# Fill in code before saving.
pre_save.connect(PasswordResetLink.pre_save, sender=PasswordResetLink,
                 dispatch_uid='profile.models')

    
def generate_code():
    return ''.join((random.choice(CODE_CHARS) for i in xrange(CODE_LENGTH)))


@receiver(user_logged_in)
def setlang(sender, **kwargs):
    try:
        translation.activate(kwargs['user'].profile.settings.language)
        kwargs['request'].session['django_language'] = translation.get_language()
    except:
        pass


class ProfilePageTag(models.Model):
    listing_type = models.CharField(max_length=100, blank=True, null=True)
    tag = models.ForeignKey(Tag, related_name='profile_tag', blank=True, null=True)
    profile = models.ForeignKey(Profile, related_name='profile')
    created_at = models.DateTimeField(auto_now_add=True)
