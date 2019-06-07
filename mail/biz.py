from django.contrib.contenttypes.models import ContentType

from .mail import Mail


def send_mail(mail_data, user):
    mail = Mail(**mail_data)
    mail.send_email(user)
    # メール送信後の処理
    content_type_id = mail_data.get('content_type')
    object_id = mail_data.get('object_id')
    if content_type_id and object_id:
        content_type = ContentType.objects.get(pk=content_type_id)
        obj = content_type.get_object_for_this_type(pk=object_id)
        if hasattr(obj, 'mail_sent_callback'):
            result = getattr(obj, 'mail_sent_callback')()
            if result:
                return result
    return None
