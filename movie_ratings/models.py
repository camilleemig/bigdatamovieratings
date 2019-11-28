from django.conf import settings
from django.db import models
from django.utils import timezone

class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.IntegerField()
    rating = models.IntegerField(null = True)