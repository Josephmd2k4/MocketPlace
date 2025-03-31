from django.db import models
import posts

class Payout(models.Model):
    payout_id = models.CharField(max_length=255, unique=True)
    email = models.EmailField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    status = models.CharField(max_length=50, default="PENDING")  # PENDING, SUCCESS, FAILED
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payout {self.payout_id} to {self.email}"