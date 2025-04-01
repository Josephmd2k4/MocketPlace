from django.db.models.signals import post_save
from django.dispatch import receiver
from posts.models import Post
from .models import Notification
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
import threading

# Thread-local variable to prevent recursion
notification_creation_in_progress = threading.local()



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