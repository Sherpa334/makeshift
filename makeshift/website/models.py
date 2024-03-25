from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    name = models.CharField(max_length = 100)
    gender = models.CharField(max_length = 50)
    location = models.CharField(max_length = 100)
    bio = models.TextField()
    likes = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
