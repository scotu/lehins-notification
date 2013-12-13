from django.utils.translation import ugettext_lazy as _
from notification.backends.base import NotificationBackend
from push_notifications.models import APNSDevice, GCMDevice
import copy
import json
import logging
from django.core.mail import send_mail
import sys

try:
    from myproject.loggers import log_event
except ImportError:
    log_event = None
error_logger = logging.getLogger("raven")

def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv

def _decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
           key = key.encode('utf-8')
        if isinstance(value, unicode):
           value = value.encode('utf-8')
        elif isinstance(value, list):
           value = _decode_list(value)
        elif isinstance(value, dict):
           value = _decode_dict(value)
        rv[key] = value
    return rv

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
        json_msg = json.loads(msg, object_hook=_decode_dict)
        
        for dev in devices:
            msg_dev = copy.copy(json_msg)
            dev_type = ""
            if isinstance(dev, APNSDevice):
                dev_type = "iOS"
                del msg_dev['msg']
            else:
                dev_type = "Android"
                del msg_dev['aps']
                
            print 'Sending notification to device: '+str(dev)
            try:
                if log_event is not None:
                    notification_dict = dict(
                        log_type="push_notification",
                        level_name="info",
                        action="sent",
                        notification_type=kwargs.get('notification_type', None),
                        device=dev_type
                    )
                    log_event(**notification_dict)
            except Exception, e:
                send_mail("Logging notification failed", str(e), "umut@eversnapapp.com", ["umut@umutgultepe.com", ], fail_silently=True)
                error_logger.error(*sys.exc_info())
            dev.send_message(msg_dev)
        return True

