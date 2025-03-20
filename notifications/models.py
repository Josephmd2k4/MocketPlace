from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from messaging.models import Message

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20)
    title = models.CharField(max_length=255)
    dm = models.PositiveIntegerField(null=True, blank=True)    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    message_text = models.TextField(null=True, blank=True)
    
    # Additional fields for marketplace-specific features
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # For price changes and offers
    location = models.CharField(max_length=255, null=True, blank=True)  # For pickup locations
    scheduled_time = models.DateTimeField(null=True, blank=True)  # For pickup scheduling

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']