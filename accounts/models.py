from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    year_in_school = models.CharField(
        max_length=10,
        choices=[
            ('Freshman', 'Freshman'),
            ('Sophomore', 'Sophomore'),
            ('Junior', 'Junior'),
            ('Senior', 'Senior'),
            ('Graduate', 'Graduate')
        ],
        blank=True,
        null=True
    )
    major = models.CharField(max_length=100, blank=True, null=True)
    profile_image = models.ImageField(blank=True, null=True)

    def __str__(self):
        return self.user.username
