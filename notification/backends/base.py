class NotificationBackend(object):
    """
    Abstract base delivery backend.
    """
    # set passive = True if backend is not capable of sending.
    passive = False

    def __unicode__(self):
        return unicode(self.title)

    @property
    def id(self):
        """
        Uniquely identify this backend delivery method with an integer powers of 2.
        """
        raise NotImplemented

    @property
    def slug(self):
        """Uniquely identify this backend delivery method."""
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
    
    @property
    def sensitivity(self):
        """spam-sensitivity for this delivery method."""
        return 2
