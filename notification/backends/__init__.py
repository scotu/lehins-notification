from django.conf import settings
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured

from notification.utils import from_string_import

NOTIFICATION_BACKENDS = getattr(settings, "NOTIFICATION_BACKENDS", 
                            ('notification.backends.email.EmailBackend',)) 

BACKENDS = []

def load_backend(path):
    try:
        cls = from_string_import(path)
    except ImportError, e:
        raise ImproperlyConfigured(
            'Error importing notification backend %s: "%s"' % (path, e))
    except ValueError, e:
        raise ImproperlyConfigured(
            'Error importing notification backends. Is NOTIFICATION_BACKENDS a '
            'correctly defined list or tuple? Error: %s' % e)
    except AttributeError:
        raise ImproperlyConfigured('Incorrect import path: %s' % path)
    if not hasattr(cls, "slug"):
        raise ImproperlyConfigured("Notification backend require a `slug` "
                                   "attribute. Please define it in %s." % cls)
    if not hasattr(cls, 'title'):
        raise ImproperlyConfigured(
            "Notification backend require a `title` "
            "attribute are deprecated. Please define it in %s." % cls)
    if getattr(cls, 'passive', False):
        return cls()
    if not hasattr(cls, 'send'):
        raise ImproperlyConfigured(
            "Notification backend require a `send` "
            "method are deprecated. Please define it in %s." % cls)
    if not callable(cls.send):
        raise ImproperlyConfigured(
            "Notification backend `send` method is not callable. "
            "Please define it in %s." % cls)
    return cls()


def get_backends(MY_BACKENDS=NOTIFICATION_BACKENDS):
    slugs = []
    BACKENDS = []
    for backend_path in MY_BACKENDS:
        backend  = load_backend(backend_path)

        if backend.slug in slugs:
            raise ImproperlyConfigured("Notification backend `slug` %s is not unique between %s and %s." %  (
                backend.slug,
                type(get_backend(backend.slug)),
                type(backend)))
        else:
            slugs.append(backend.slug)
            BACKENDS.append(backend)
    return BACKENDS


def get_backend(slug):
    for b in get_backends():
        if b.slug == slug:
            return b
    raise ValueError("Notification backend for slug %s not found. Is NOTIFICATION_BACKENDS correctly defined?" % slug)


