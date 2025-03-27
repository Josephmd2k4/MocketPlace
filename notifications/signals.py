from django.db.models.signals import post_save
from django.dispatch import receiver
from posts.models import Post
from .models import Notification
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
import threading

# Thread-local variable to prevent recursion
notification_creation_in_progress = threading.local()

# To prevent recursion, you can add a flag to check if the notification was already created by the first signal
@receiver(post_save, sender=Post)
def notify_users_on_new_post(sender, instance, created, **kwargs):
    if created:
        users_to_notify = User.objects.exclude(id=instance.user.id)
        for user in users_to_notify:
            # Prevent creating a notification again in case it's already created by the first signal
            notification = Notification.objects.create(
                recipient=user,
                sender=instance.user,
                notification_type='POST',
                title=f'New Post: {instance.title[:50]}',
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id,
                is_read=False
            )
            # You can add some check here to avoid unnecessary recursion


@receiver(post_save, sender=Notification)
def notify_users_on_new_message(sender, instance, created, **kwargs):
    # Prevent recursion by checking if the flag is set
    if getattr(notification_creation_in_progress, 'flag', False):
        print("Skipping notification creation to avoid recursion.")
        return

    if created and instance.notification_type == 'DM':  # Avoid recursion by checking notification type
        # Flag set to prevent recursion
        notification_creation_in_progress.flag = True

        # Reset the flag after processing
        notification_creation_in_progress.flag = False