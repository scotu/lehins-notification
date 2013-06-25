from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.translation import ugettext_lazy as _

from notification.backends.base import NotificationBackend
from HTMLParser import HTMLParser

class EmailBackend(NotificationBackend):
    """
    Email delivery backend.
    """
    id = 4
    title = _("By Email")
    slug = 'email'
    formats = ('subject.txt', 'message.txt')

    def get_addresses(self, recipients):
        addresses = []
        try:
            iter_recipients = iter(recipients)
        except TypeError:
            iter_recipients = iter([recipients])
        for recipient in iter_recipients:
            address = getattr(recipient, 'email', None)
            if address:
                addresses.append(address)

        return addresses

    def send(self, message, recipients, *args, **kwargs):
        subject = ' '.join(message['subject.txt'].splitlines())
        body = message['message.txt']
        addresses = self.get_addresses(recipients)
        if addresses:
            return send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, addresses)


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)


class HTMLEmailBackend(EmailBackend):
    """
    Email delivery backend with html support as alternative content.
    """
    
    formats = ('subject.txt', 'message.html')

    def _strip_tags(self, html):
        s = MLStripper()
        s.feed(html)
        return s.get_data()

    def send(self, messages, recipients, *args, **kwargs):
        addresses = self.get_addresses(recipients)
        if addresses:
            subject = ' '.join(messages['subject.txt'].splitlines())
            body_html = messages['message.html']
            body = self._strip_tags(body_html)
            email = EmailMultiAlternatives(
                subject, body, settings.DEFAULT_FROM_EMAIL, addresses)
            email.attach_alternative(body_html, "text/html")
            email.send()
            return email

