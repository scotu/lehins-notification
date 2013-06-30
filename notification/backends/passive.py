from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.translation import ugettext_lazy as _

from notification.backends.base import NotificationBackend

class OnSiteBackend(NotificationBackend):
    """
    On Site passive backend.
    """
    id = 2
    passive = True
    title = _("On Site")
    slug = 'on_site'
    sensitivity = 1
