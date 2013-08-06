from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.translation import ugettext_lazy as _

from notification.backends.base import NotificationBackend
from HTMLParser import HTMLParser


class EmailBackend(NotificationBackend):
    """
    Email delivery backend.
    """
    
    title = _("Email")
    slug = 'email'
    formats = ('subject.txt', 'message.txt')

    def get_addresses(self, recipients):
        addresses = []
        for recipient in recipients:
            addresse = getattr(recipient, 'email', None)
            if addresse:
                addresses.append(addresse)

        return addresses

    def send(self, message, recipients, *args, **kwargs):
        subject = ' '.join(message['subject.txt'].splitlines())
        body = message['message.txt']
        addresses = self.get_addresses(recipients)
        if addresses:
            user_sender = kwargs.pop('overwrite_sender', False)
            if user_sender:
                try:
                    if user_sender.firstName:
                        sender_email = '%s <%s>' % (user_sender.firstName, user_sender.email,)
                    else:
                        sender_email = user_sender.email
                except:
                    sender_email = settings.DEFAULT_FROM_EMAIL
            else:
                sender_email = settings.DEFAULT_FROM_EMAIL
            return send_mail(subject, body, sender_email, addresses)


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
        subject = ' '.join(messages['subject.txt'].splitlines())
        body_html = messages['message.html']
        body = self._strip_tags(body_html)
        addresses = self.get_addresses(recipients)
        if addresses:
            notification_type = ''
            if 'notification_type' in kwargs:
                notification_type = kwargs.pop('notification_type')

            user_sender = kwargs.pop('overwrite_sender', False)
            if user_sender:
                try:
                    if user_sender.firstName:
                        sender_email = '%s <%s>' % (user_sender.firstName, user_sender.email,)
                    else:
                        sender_email = user_sender.email
                except:
                    sender_email = settings.DEFAULT_FROM_EMAIL
            else:
                sender_email = settings.DEFAULT_FROM_EMAIL

            email = EmailMultiAlternatives(
                subject, body, sender_email, addresses)
            if notification_type:
                email.extra_headers = {'X-SMTPAPI':'{"category": "%s"}' % notification_type}
            email.attach_alternative(body_html, "text/html")
            print 'Sending email to: ' + str(addresses)
            while True:
                try:
                    email.send()
                    print 'Email Sent Ok!'
                    break
                except:
                    print 'Waiting to try again'
                    import time; time.sleep(4)

            return email

