import importlib

from django.conf import settings
from django.contrib.sites.models import Site
from django.template import Context
from django.template.loader import render_to_string



USE_SSL = getattr(settings, "NOTIFICATION_USE_SSL", False)
CONTEXT_PROCESSORS = getattr(settings, "NOTIFICATION_CONTEXT_PROCESSORS", [])


def from_string_import(string):
    """
    Returns the attribute from a module, specified by a string.
    """
    module, attrib = string.rsplit('.', 1)
    return getattr(importlib.import_module(module), attrib)

def apply_context_processors(context):
    for cp in [from_string_import(x) for x in CONTEXT_PROCESSORS]:
        context.update(cp())
    return context

def get_formatted_message(formats, notice_type, context, medium):
    """
    Returns a dictionary with the format identifier as the key. The values are
    are fully rendered templates with the given context.
    """
    if not isinstance(context, Context):
        context = Context(context or {})
    protocol = 'https' if USE_SSL else 'http'
    current_site = Site.objects.get_current()
    base_url = u"%s://%s" % (protocol, unicode(current_site))
    context.update({
        'base_url': base_url,
        'site': current_site,
    })
    format_templates = {}
    context = apply_context_processors(context)
    for format in formats:
        # conditionally turn off autoescaping for .txt extensions in format
        if format.endswith(".txt") or format.endswith(".html"):
            context.autoescape = False
        else:
            context.autoescape = True
        format_templates[format] = render_to_string((
            'notification/%s/%s/%s' % (
                    notice_type.template_slug, medium, format),
            'notification/%s/%s' % (notice_type.template_slug, format),
            'notification/%s/%s' % (medium, format),
            'notification/%s' % format), context_instance=context)
    return format_templates
