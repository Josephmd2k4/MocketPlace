from django.db import models
from django.contrib.auth.models import User
from webpush.models import PushInformation

class userEnabledNotifs(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    push_info = models.OneToOneField(PushInformation, on_delete=models.CASCADE)