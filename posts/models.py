from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

class Post(models.Model):
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
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='posts/images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return self.title