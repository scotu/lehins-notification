import celery

from notification.backends import get_backend
from notification.utils import get_formatted_message


@celery.task
def send_notice(notice, notice_settings, context):
    context = context or {}
    context.update({'notice': notice,
                    'recipient': notice.recipient,
                    'sender': notice.sender,
                    'related_object': notice.related_object,
                    'notice_type': notice.notice_type})
    for setting in notice_settings:
        backend = get_backend(setting.medium)
        # get prerendered format messages
        context.update({'notice_setting': setting})
        message = get_formatted_message(
            backend.formats, notice.notice_type, context, backend.slug)
        backend.send(message, notice.recipient)
