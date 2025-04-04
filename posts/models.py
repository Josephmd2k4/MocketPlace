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
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

class Media(models.Model):
    post = models.ForeignKey('Post', related_name='media_set', on_delete=models.CASCADE)
    file = models.FileField(upload_to='posts/media/')
    created_at = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
     
    def __str__(self):
        return self.title