from django.db.models.signals import post_save
from django.dispatch import receiver
from posts.models import Post
from .models import Notification
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

@receiver(post_save, sender=Post)
def notify_users_on_new_post(sender, instance, created, **kwargs):
    if created:
        users_to_notify = User.objects.exclude(id=instance.author.id)
        for user in users_to_notify:
            Notification.objects.create(
                recipient=user,
                sender=instance.author,
                notification_type='POST',
                title=f'New Post: {instance.title[:50]}',
                message=f'{instance.author.username} has created a new post',
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id,
                is_read=False
            )

@receiver(post_save, sender=Notification)
def notify_users_on_new_message(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.recipient,
            sender=instance.sender,
            notification_type='DM',
            title=f'New Message from {instance.sender.username}',
            message=instance.message,
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id,
            is_read=False
        )