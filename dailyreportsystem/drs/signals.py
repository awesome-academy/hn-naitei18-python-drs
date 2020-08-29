from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.template.loader import render_to_string
from django.core.mail import send_mail,EmailMessage

from .models import Form, Report, Notification, User

@receiver(post_save, sender=Form)
def create_notification(sender, instance, created, **ksargs):
    if created:
        noti_receiver = instance.receiver
        noti_sender = instance.sender
        noti_form_id = instance
        noti_type = "nr"
        noti_content = "New request: {}".format(instance.title)
        noti_created_at = timezone.now()
        Notification.objects.create(sender=noti_sender, receiver=noti_receiver, created_at=noti_created_at,
                                    form_id=noti_form_id, type_notification=noti_type, content=noti_content)

# @receiver(post_save, sender=Notification)
# def send_notification_info(sender, instance, created, **ksargs):
#     if created:
#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_send)(
#             "notification_group_{}".format(instance.sender.id), {
#                 'type':'notification_info'
#             }
#         )

@receiver(post_save, sender=Notification)
def send_mail_when_has_new_form(sender, instance, created, **ksargs):
    if created:
        mail_subject = "Request Notification"
        message = render_to_string('notification/notification_form_mail.html', {
				'noti_title': instance.content,
			})
        to_email = instance.receiver.email
        email = EmailMessage(
            mail_subject, message, to=[to_email],
        )
        email.content_subtype = "html"
        email.send()
