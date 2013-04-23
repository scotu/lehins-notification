from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.translation import ugettext_lazy as _

from notification.backends.base import NotificationBackend
from HTMLParser import HTMLParser
from push_notifications import APNSDevice, GCMDevice
import json

class MobileBackend(NotificationBackend):
    """
    Mobile (IOS/Android) delivery backend.
    """

    title = _("Mobile")
    slug = 'mobile'
    formats = ('message.txt',)

    def get_devices(self, recipients):
        devices = []
        for recipient in recipients:
            for dev_ios in APNSDevice.objects.filter(user=recipient):
                devices.append(dev_ios)
            for dev_android in GCMDevice.objects.filter(user=recipient):
                devices.append(dev_android)

        return devices

    def send(self, message, recipients, *args, **kwargs):
        msg = message['message.txt']
        devices = self.get_devices(recipients)
        for dev in devices:
            dev.send_message(msg)

        return True

