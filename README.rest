######################################################################
lehins-notification - notification app for django
######################################################################
Forked from `incuna-notification <https://github.com/incuna/incuna-notification>`_, which is a fork of a `django-notification <https://github.com/jtauber/django-notification>`_

**Compatibility:**

It is backwards compatible with incuna-notification, except the backend specification.

**Usage:**

* Original usage documentation is in docs/usage.txt

**Added features:**

* ``HTMLEmailBackend`` that supports html email content as an alternative
* backends can specify names for the templates, so they are no longer limited only to ``message.txt`` and ``subject.txt``. ``notice.html`` is the only (in case of empty backend list) required template
* Can specify context processors for email rendering with ``NOTIFICATION_CONTEXT_PROCESSORS`` setting, which are just like django context processors, except they don't have request argument
* Removed a bug in views NOTICE_MEDIA did not exist.

**Backend usage changes:**

* required ``formats`` property, which is a list of template names, relevant to a
  message.
* ``send`` method takes ``message`` argument, instead of subject and body
  strings. ``message`` now is a dictonary of rendered templates specified in 
  ``formats`` property, having there names as keys. See supplied backends for 
  examples.

**Coming soon:**
* support for scheduling notifications using celery
