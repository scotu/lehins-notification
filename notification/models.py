import hashlib
from uuid import uuid4 as uuid_generator

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User as AuthUser
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from notification.backends import get_backends, get_backend
from notification.tasks import send_notice


__all__ = ["NoticeType", "NoticeSetting", "Notice", "send"]

CONTEXT_PROCESSORS = getattr(
    settings, "NOTIFICATION_CONTEXT_PROCESSORS", None)

DELAY_ALL = getattr(settings, "NOTIFICATION_DELAY_ALL", True)

ENFORCE_CREATE = getattr(settings, "NOTIFICATION_ENFORCE_CREATE", False)

User = getattr(settings, 'AUTH_USER_MODEL', AuthUser)


class NoticeType(models.Model):

    label = models.CharField(_('label'), max_length=40, unique=True)
    display = models.CharField(_('display'), max_length=100)
    description = models.TextField(_('description'))

    # by default only on for media with sensitivity less than or equal to this number
    default = models.SmallIntegerField(_('default'), default=2)
    
    allowed = models.SmallIntegerField(
        verbose_name=u"Allowed", default=6, help_text=u"Sum of the media type's "
        "ids stored in backends dictate if the particular medium notification "
        "can be switch off/on by a user. Currently 2-on_site, 4-email")

    def __unicode__(self):
        return self.label


    class Meta:
        ordering = ["label"]
        verbose_name = _("notice type")
        verbose_name_plural = _("notice types")

    @property
    def template_slug(self):
        return self.label


class NoticeMediaListChoices():
    """
    Iterator used to delay getting the NoticeSetting medium choices list until 
    required (and when the other medium have been registered).
    """

    def __init__(self):
        self.index = -1

    def __iter__(self):
        return self

    def next(self):
        self.index += 1
        if self.index == 0:
            return ('on_site', "On Site")
        try:
            item = get_backends()[self.index-1]
            return (item.slug, item.title)
        except IndexError:
            raise StopIteration


class NoticeSettingManager(models.Manager):

    def get_or_create(self, user, notice_type, medium, **kwargs):
        kwargs.update({
            'user': user,
            'notice_type': notice_type,
            'medium': medium
        })
        return super(NoticeSettingManager, self).get_or_create(**kwargs)

    def filter_or_create(self, user, notice_type_or_label):
        """
        Gets NoticeSettings for notification_label and user for all medium 
        registered. Creats Default ones if there is nothing.
        Raises DoesNotExist for wrong label.
        """
        result = self.filter(user=user)
        if isinstance(notice_type_or_label, NoticeType):
            notice_type = notice_type_or_label
            result = result.filter(notice_type=notice_type)
        else:
            notice_type = None
            result = result.filter(notice_type__label=notice_type_or_label)
        media_choices = list(NoticeMediaListChoices())
        if len(result) != len(media_choices):
            notice_type = notice_type or NoticeType.objects.get(
                label=notice_type_or_label)
            for slug, medium in media_choices:
                self.get_or_create(user=user, notice_type=notice_type, medium=slug)
            result = self.filter(user=user, notice_type=notice_type)
        return result


class NoticeSetting(models.Model):
    """
    Indicates, for a given user, whether to send notifications
    of a given type to a given medium.
    """
    @classmethod
    def _generate_uuid(cls):
        while True:
            uuid = uuid_generator()
            try:
                cls.objects.get(uuid=uuid)
            except cls.DoesNotExist:
                return uuid

    user = models.ForeignKey(User, verbose_name=_('user'))
    notice_type = models.ForeignKey(NoticeType, verbose_name=_('notice type'))
    medium = models.CharField(
        _('medium'), max_length=100, choices=NoticeMediaListChoices())
    send = models.BooleanField(_('send'))
    uuid = models.CharField(
        _('uuid'), max_length=36, editable=False, default=uuid_generator)

    objects = NoticeSettingManager()

    @property
    def token(self):
        return hashlib.sha1(self.user.email+self.notice_type.label).hexdigest()

    @property
    def can_modify(self):
        return bool(get_backend(self.medium).id & self.notice_type.allowed)

    def __init__(self, *args, **kwargs):
        medium = kwargs.get('medium', None)
        notice_type = kwargs.get('notice_type', None)
        if medium and notice_type and 'send' not in kwargs:
            kwargs['send'] = (get_backend(medium).sensitivity <= notice_type.default)
        super(NoticeSetting, self).__init__(*args, **kwargs)


    def __unicode__(self):
        return self.medium

    def get_absolute_url(self):
        return reverse("notification:notice_setting", kwargs={
            'pk': self.pk, 'token': self.token, 'uuid': self.uuid})


    class Meta:
        verbose_name = _("notice setting")
        verbose_name_plural = _("notice settings")
        unique_together = ("user", "notice_type", "medium")


class NoticeManager(models.Manager):

    def notices_for(self, user, **kwargs):
        """
        returns Notice objects for the given user.

        If archived=False, it only include notices not archived.
        If archived=True, it returns all notices for that user.

        If unseen=None, it includes all notices.
        If unseen=True, return only unseen notices.
        If unseen=False, return only seen notices.
        """
        sent = kwargs.pop('sent', False)
        if sent:
            lookup_kwargs = {"sender": user}
        else:
            lookup_kwargs = {"recipient": user}
        return self.filter(**lookup_kwargs).filter(**kwargs)

    def unseen_count_for(self, recipient):
        """
        returns the number of unseen notices for the given user but does not
        mark them seen
        """
        return self.notices_for(recipient, unseen=True, on_site=True).count()
    
    def received(self, recipient, **kwargs):
        """
        returns notices the given recipient has recieved.
        """
        kwargs["sent"] = False
        return self.notices_for(recipient, **kwargs)
    
    def sent(self, sender, **kwargs):
        """
        returns notices the given sender has sent
        """
        kwargs["sent"] = True
        return self.notices_for(sender, **kwargs)

class Notice(models.Model):

    recipient = models.ForeignKey(User, related_name='recieved_notices', verbose_name=_('recipient'))
    sender = models.ForeignKey(User, null=True, related_name='sent_notices', verbose_name=_('sender'))
    notice_type = models.ForeignKey(NoticeType, verbose_name=_('notice type'))
    added = models.DateTimeField(_('added'), auto_now_add=True)
    unseen = models.BooleanField(_('unseen'), default=True)
    archived = models.BooleanField(_('archived'), default=False)
    on_site = models.BooleanField(_('on site'))
    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.PositiveIntegerField(null=True)
    related_object = generic.GenericForeignKey('content_type', 'object_id')

    objects = NoticeManager()

    def __unicode__(self):
        return self.message

    def archive(self, commit=True):
        self.archived = True
        if commit:
            self.save()

    def is_unseen(self):
        """
        returns value of self.unseen but also changes it to false.

        Use this in a template to mark an unseen notice differently the first
        time it is shown.
        """
        unseen = self.unseen
        if unseen:
            self.unseen = False
            self.save()
        return unseen

    class Meta:
        ordering = ["-added"]
        verbose_name = _("notice")
        verbose_name_plural = _("notices")

    def get_absolute_url(self):
        return reverse("notification:notice", kwargs={'pk': self.pk})


def smart_send(users, label, extra_context=None, sender=None, related_object=None, 
               now=True):
    """
    Creates a new notice.

    This is intended to be how other apps create new notices.

    notification.send(user, 'friends_invite_sent', {
        'spam': 'eggs',
        'foo': 'bar',
    })
    
    You can pass in on_site=False to prevent the notice emitted from being
    displayed on the site.
    """
    try:
        iter_users = iter(users)
    except TypeError:
        iter_users = iter([users])
    for user in iter_users:
        notice_type = NoticeType.objects.get(label=label)
        notice_settings = NoticeSetting.objects.filter_or_create(
            user, notice_type).filter(send=True)
        if notice_settings:
            active_settings = []
            on_site = False
            for setting in notice_settings:
                if not get_backend(setting.medium).passive:
                    active_settings.append(setting)
                elif setting.medium == 'on_site':
                    on_site = True
            notice = Notice.objects.create(
                recipient=user, notice_type=notice_type,
                on_site=on_site, sender=sender, related_object=related_object)
            if active_settings and user.is_active:
                if now or not DELAY_ALL:
                    send_notice(notice, active_settings, extra_context)
                else:
                    send_notice.delay(notice, active_settings, extra_context)
        elif ENFORCE_CREATE:
            Notice.objects.create(
                recipient=user, notice_type=notice_type,
                on_site=False, sender=sender, related_object=related_object)

def send(*args, **kwargs):
    extra_context = kwargs.get('extra_context', None)
    if extra_context:
        # for compatibility with postman
        if 'pm_message' in extra_context:
            kwargs['related_object'] = extra_context['pm_message']
    return smart_send(*args, **kwargs)


# methods below are left purely for backward compatibility

def create_notice_type(label, display, description, default=2, verbosity=1, slug=''):
    kwargs = {'label': label,
              'display': display,
              'description': description,
              'default': default}
    notice_type_qs = NoticeType.objects.filter(label=label)
    if notice_type_qs:
        notice_type_qs.update(**kwargs)
        if verbosity > 1:
            print "Updated %s NoticeType" % label
    else:
        NoticeType.objects.create(**kwargs)
        if verbosity > 1:
            print "Created %s NoticeType" % label

def create_notification_setting(user, notice_type, medium):
    return NoticeSetting.objects.create(
        user=user, notice_type=notice_type, medium=medium)

def get_notification_setting(user, notice_type, medium):
    setting, created = NoticeSetting.objects.get_or_create(
        user, notice_type, medium)
    return setting


def get_notification_settings(user, notification_label):
    return NoticeSetting.objects.filter_or_create(user, notification_label)

def should_send(user, notice_type, medium):
    return get_notification_setting(user, notice_type, medium).send
