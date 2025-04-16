from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    def __str__(self):
        return f'Профиль {self.user.username}'
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)