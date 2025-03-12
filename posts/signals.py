from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Post
from notifications.views import send_post_notification

@receiver(post_save, sender=Post)
def new_post(sender, instance, created, **kwargs):
    if created:
        request = None  # You need to pass the request object if required
        send_post_notification(request, instance.id)