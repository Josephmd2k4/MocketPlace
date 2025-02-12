from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('DM', 'Direct Message'),
        ('POST', 'New Item Posted'),
        ('PRICE', 'Price Change'),
        ('OFFER', 'New Offer'),
        ('COUNTER', 'Counter Offer'),
        ('ACCEPT', 'Offer Accepted'),
        ('REJECT', 'Offer Rejected'),
        ('SAVED', 'Item Back in Stock'),
        ('COMMENT', 'New Comment'),
        ('RESERVED', 'Item Reserved'),
        ('SOLD', 'Item Sold'),
        ('PICKUP', 'Pickup Arranged'),
        ('REVIEW', 'New Review'),
        ('VERIFIED', 'Account Verified'),
        ('WARNING', 'Safety Warning'),
    )

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_received')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_sent')
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # For generic relations (connecting to items, offers, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Additional fields for marketplace-specific features
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # For price changes and offers
    location = models.CharField(max_length=255, null=True, blank=True)  # For pickup locations
    scheduled_time = models.DateTimeField(null=True, blank=True)  # For pickup scheduling

    class Meta:
        ordering = ['-created_at']