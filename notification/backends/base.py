class NotificationBackend(object):
    """
    Abstract base delivery backend.
    """

    def __unicode__(self):
        return unicode(self.title)

    @property
    def slug(self):
        """Uniquely identify this backenddelivery method."""
        raise NotImplemented

    @property
    def title(self):
        """Pretty name for this delivery method."""
        raise NotImplemented

    @property
    def formats(self):
        """List of template names that will be rendered."""
        raise NotImplemented

    def send(self, message, recipients, *args, **kwargs):
        """
        Send the notification.
        """
        raise NotImplemented

    def sensitivity(self):
        """spam-sensitivity for this delivery method."""
        return 2
