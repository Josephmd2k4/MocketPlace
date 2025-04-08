from django.db import models

class Payout(models.Model):
    payout_batch_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_synced = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, default="PENDING")  # PENDING, SUCCESS, FAILED

    def __str__(self):
        return f"Payout {self.payout_batch_id} to {self.email}"