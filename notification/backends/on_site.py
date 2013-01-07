from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.translation import ugettext_lazy as _

from notification.backends.base import NotificationBackend
from HTMLParser import HTMLParser

class OnSiteBackend(NotificationBackend):
    """
    Email delivery backend.
    """
    
    title = _("On Site")
    slug = 'on_site'
    formats = ('notice.html',)

    def send(self, *args, **kwargs):
        pass

