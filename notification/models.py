import hashlib
from uuid import uuid4 as uuid_generator

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
<<<<<<< HEAD
from django.template import Context
from django.template.loader import render_to_string

from django.core.exceptions import ImproperlyConfigured

from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
=======
from django.contrib.auth.models import User as AuthUser
>>>>>>> 077f6d8bea0d51fda082fee14def15a51899c393
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.template.base import Template, Context
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from notification.backends import get_backends, get_backend
from notification.tasks import send_notice
from notification.utils import apply_context_processors

__all__ = ["NoticeType", "NoticeSetting", "Notice", "send"]


<<<<<<< HEAD
QUEUE_ALL = getattr(settings, "NOTIFICATION_QUEUE_ALL", False)
USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
=======
DELAY_ALL = getattr(settings, "NOTIFICATION_DELAY_ALL", True)
>>>>>>> 077f6d8bea0d51fda082fee14def15a51899c393

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
    template = models.TextField(
        blank=True, help_text="Template that will be used in rendering the notice.")

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
<<<<<<< HEAD
    user = models.ForeignKey(USER_MODEL, verbose_name=_("user"))
=======
    @classmethod
    def _generate_uuid(cls):
        while True:
            uuid = uuid_generator()
            try:
                cls.objects.get(uuid=uuid)
            except cls.DoesNotExist:
                return uuid

    user = models.ForeignKey(User, verbose_name=_('user'))
>>>>>>> 077f6d8bea0d51fda082fee14def15a51899c393
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
        if 'archived' not in kwargs:
            lwargs['archived'] = False
        return self.filter(**lookup_kwargs).filter(**kwargs)

    def unseen_count_for(self, recipient):
        """
        returns the number of unseen notices for the given user but does not
        mark them seen
        """
<<<<<<< HEAD
        return self.notices_for(recipient, unseen=True, **kwargs).count()

=======
        return self.notices_for(
            recipient, unseen=True, on_site=True, archived=False).count()
    
>>>>>>> 077f6d8bea0d51fda082fee14def15a51899c393
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
<<<<<<< HEAD
    recipient = models.ForeignKey(USER_MODEL, related_name="recieved_notices", verbose_name=_("recipient"))
    sender = models.ForeignKey(USER_MODEL, null=True, related_name="sent_notices", verbose_name=_("sender"))
    message = models.TextField(_('message'))
=======

    recipient = models.ForeignKey(User, related_name='recieved_notices', verbose_name=_('recipient'))
    sender = models.ForeignKey(User, null=True, related_name='sent_notices', verbose_name=_('sender'))
>>>>>>> 077f6d8bea0d51fda082fee14def15a51899c393
    notice_type = models.ForeignKey(NoticeType, verbose_name=_('notice type'))
    added = models.DateTimeField(_('added'), auto_now_add=True)
    unseen = models.BooleanField(_('unseen'), default=True)
    archived = models.BooleanField(_('archived'), default=False)
    on_site = models.BooleanField(_('on site'))
    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.PositiveIntegerField(null=True)
    related_object = generic.GenericForeignKey('content_type', 'object_id')

    objects = NoticeManager()

    def __str__(self):
        return self.notice_type.description

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

    def render(self):
        template = Template(self.notice_type.template, name=self.notice_type.label)
        context = apply_context_processors({'notice':self})
        return mark_safe(template.render(Context(context)))

    def get_absolute_url(self):
        return reverse("notification:notice", kwargs={'pk': self.pk})

    class Meta:
        ordering = ["-added"]
        verbose_name = _("notice")
        verbose_name_plural = _("notices")

<<<<<<< HEAD
    def get_absolute_url(self):
        return reverse("notification_notice", args=[str(self.pk)])

    def get_absolute_url(self):
        return ("notification_notice", [str(self.pk)])
    get_absolute_url = models.permalink(get_absolute_url)


class NoticeQueueBatch(models.Model):
    """
    A queued notice.
    Denormalized data for a notice.
    """
    pickled_data = models.TextField()


def create_notice_type(label, display, description, default=2, verbosity=1, slug=''):
    """
    Creates a new NoticeType.

    This is intended to be used by other apps as a post_syncdb manangement step.
    """
    try:
        notice_type = NoticeType.objects.get(label=label)
        updated = False
        if display != notice_type.display:
            notice_type.display = display
            updated = True
        if description != notice_type.description:
            notice_type.description = description
            updated = True
        if default != notice_type.default:
            notice_type.default = default
            updated = True
        if slug != notice_type.slug:
            notice_type.slug = slug
            updated = True
        if updated:
            notice_type.save()
            if verbosity > 1:
                print "Updated %s NoticeType" % label
    except NoticeType.DoesNotExist:
        notice_type = NoticeType.objects.create(label=label, display=display, description=description, default=default, slug=slug)
        if verbosity > 1:
            print "Created %s NoticeType" % label
    return notice_type

def get_notification_language(user):
    """
    Returns site-specific notification language for this user. Raises
    LanguageStoreNotAvailable if this site does not use translated
    notifications.
    """
    if getattr(settings, 'NOTIFICATION_LANGUAGE_MODULE', False):
        try:
            app_label, model_name = settings.NOTIFICATION_LANGUAGE_MODULE.split('.')
            model = models.get_model(app_label, model_name)
            language_model = model._default_manager.get(user__id__exact=user.id)
            if hasattr(language_model, 'language'):
                return language_model.language
        except (ImportError, ImproperlyConfigured, model.DoesNotExist):
            raise LanguageStoreNotAvailable
    raise LanguageStoreNotAvailable

def from_string_import(string):
    """
    Returns the attribute from a module, specified by a string.
    """
    module, attrib = string.rsplit('.', 1)
    return getattr(importlib.import_module(module), attrib)


def get_formatted_message(formats, notice_type, context, media_slug=None):
    """
    Returns a dictionary with the format identifier as the key. The values are
    are fully rendered templates with the given context.
    """
    format_templates = {}
    if context is None:
        context = {}
    if CONTEXT_PROCESSORS:
        for c_p in [from_string_import(x) for x in CONTEXT_PROCESSORS]:
            context.update(c_p())
    for format in formats:
        # conditionally turn off autoescaping for .txt extensions in format
        if format.endswith(".txt") or format.endswith(".html"):
            context.autoescape = False
        else:
            context.autoescape = True
        format_templates[format] = render_to_string((
            'notification/%s/%s/%s' % (
                    notice_type.template_slug, media_slug, format),
            'notification/%s/%s' % (notice_type.template_slug, format),
            'notification/%s/%s' % (media_slug, format),
            'notification/%s' % format), context_instance=context)
    return format_templates

def send_now(users, label, extra_context=None, on_site=None, sender=None, related_object_id=None, backends=get_backends()):
=======

def smart_send(users, label, extra_context=None, sender=None, related_object=None, 
               now=False):
>>>>>>> 077f6d8bea0d51fda082fee14def15a51899c393
    """
    Creates a new notice.

    This is intended to be how other apps create new notices.

<<<<<<< HEAD
    notification.send(user, "friends_invite_sent", {
        "spam": "eggs",
        "foo": "bar",
    )

    You can pass in on_site=False to prevent the notice emitted from being
    displayed on the site.
    """
    if extra_context is None:
        extra_context = {}

    notice_type = NoticeType.objects.get(label=label)

    protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
    current_site = Site.objects.get_current()

    current_language = get_language()

    for user in users:
        # get user language for user from language store defined in
        # NOTIFICATION_LANGUAGE_MODULE setting
        try:
            language = get_notification_language(user)
        except LanguageStoreNotAvailable:
            language = None

        if language is not None:
            # activate the user's language
            activate(language)

        # update context with user specific translations
        context = Context({
            "recipient": user,
            "sender": sender,
            "notice": ugettext(notice_type.display),
            "current_site": current_site,
        })
        context.update(extra_context)
        
        messages = get_formatted_message(
            ['notice.html'], notice_type, context, 'notice')
        notice_setting = get_notification_setting(user, notice_type, 'email')
        if on_site is None:
            on_site = notice_setting.on_site
        notice = Notice.objects.create(
            recipient=user, message=messages['notice.html'], notice_type=notice_type,
            on_site=on_site, sender=sender, related_object_id=related_object_id)

        if len(backends) > 0 and isinstance(backends[0], str):
            backends = get_backends(backends)

        for backend in backends:
            send_user_notification(user, notice_type, backend, context)

    # reset environment to original language
    activate(current_language)

def send_user_notification(user, notice_type, backend, context):

    recipients = []

    # get prerendered format messages
    message = get_formatted_message(
        backend.formats, notice_type, context, backend.slug)

    if user.is_active and should_send(user, notice_type, backend.slug):
        recipients.append(user)

    if recipients:
        try:
            kwargs = {}
            kwargs['notification_type'] = notice_type.label
            if 'sender_album_code' in context and context['sender_album_code']:
                kwargs['sender_album_code'] = context.get('sender_album_code')
            if 'sender_album_title' in context and context['sender_album_title']:
                kwargs['sender_album_title'] = context.get('sender_album_title')
            if 'reply_to' in context and context['reply_to']:
                kwargs['overwrite_reply_to'] = context.get('reply_to')
            backend.send(message, recipients, **kwargs)
        except TypeError, e:
            print u"Tried to send notification to media %s. Send function raised an error." % (backend.title,)
            raise e

=======
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
                elif setting.medium == 'on_site' and setting.send:
                    on_site = True
            notice = Notice.objects.create(
                recipient=user, notice_type=notice_type,
                on_site=on_site, sender=sender, related_object=related_object)
            if active_settings and user.is_active:
                if now or not DELAY_ALL:
                    send_notice(notice, active_settings, extra_context)
                else:
                    send_notice.apply_async(
                        args=(notice, active_settings, extra_context), 
                        countdown=10)
        elif ENFORCE_CREATE:
            Notice.objects.create(
                recipient=user, notice_type=notice_type,
                on_site=False, sender=sender, related_object=related_object)
>>>>>>> 077f6d8bea0d51fda082fee14def15a51899c393

def send(*args, **kwargs):
    extra_context = kwargs.get('extra_context', None)
    if extra_context:
        # for compatibility with postman
        if 'pm_message' in extra_context:
            kwargs['related_object'] = extra_context['pm_message']
            kwargs['sender'] = extra_context['pm_message'].sender
    return smart_send(*args, **kwargs)


<<<<<<< HEAD
    def all_for(self, observed, signal):
        """
        Returns all ObservedItems for an observed object,
        to be sent when a signal is emited.
        """
        content_type = ContentType.objects.get_for_model(observed)
        observed_items = self.filter(content_type=content_type, object_id=observed.id, signal=signal)
        return observed_items

    def get_for(self, observed, observer, signal):
        content_type = ContentType.objects.get_for_model(observed)
        observed_item = self.get(content_type=content_type, object_id=observed.id, user=observer, signal=signal)
        return observed_item


class ObservedItem(models.Model):
    user = models.ForeignKey(USER_MODEL, verbose_name=_("user"))

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    observed_object = generic.GenericForeignKey('content_type', 'object_id')

    notice_type = models.ForeignKey(NoticeType, verbose_name=_('notice type'))

    added = models.DateTimeField(_('added'), auto_now_add=True)

    # the signal that will be listened to send the notice
    signal = models.TextField(verbose_name=_('signal'))

    objects = ObservedItemManager()

    class Meta:
        ordering = ["-added"]
        verbose_name = _("observed item")
        verbose_name_plural = _("observed items")

    def send_notice(self, extra_context=None):
        if extra_context is None:
            extra_context = {}
        extra_context.update({'observed': self.observed_object})
        send([self.user], self.notice_type.label, extra_context)

def observe(observed, observer, notice_type_label, signal='post_save'):
    """
    Create a new ObservedItem.
=======
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
>>>>>>> 077f6d8bea0d51fda082fee14def15a51899c393

def create_notification_setting(user, notice_type, medium):
    return NoticeSetting.objects.create(
        user=user, notice_type=notice_type, medium=medium)

def get_notification_setting(user, notice_type, medium):
    setting, created = NoticeSetting.objects.get_or_create(
        user, notice_type, medium)
    return setting

<<<<<<< HEAD
def send_observation_notices_for(observed, signal='post_save', extra_context=None):
    """
    Send a notice for each registered user about an observed object.
    """
    if extra_context is None:
        extra_context = {}
    observed_items = ObservedItem.objects.all_for(observed, signal)
    for observed_item in observed_items:
        observed_item.send_notice(extra_context)
    return observed_items


def is_observing(observed, observer, signal="post_save"):
    if hasattr(observer, 'is_anonymous') and observer.is_anonymous():
        return False
    try:
        observed_items = ObservedItem.objects.get_for(observed, observer, signal)
        return True
    except ObservedItem.DoesNotExist:
        return False
    except ObservedItem.MultipleObjectsReturned:
        return True
=======
>>>>>>> 077f6d8bea0d51fda082fee14def15a51899c393

def get_notification_settings(user, notification_label):
    return NoticeSetting.objects.filter_or_create(user, notification_label)

def should_send(user, notice_type, medium):
    return get_notification_setting(user, notice_type, medium).send
