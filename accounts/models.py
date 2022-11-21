from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator,MinValueValidator


class Activation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True)

    

# Model to store the list of logged in users
class LoggedInUser(models.Model):
    user = models.OneToOneField(User, on_delete= models.CASCADE , related_name='logged_in_user')
    # Session keys are 32 characters long
    session_key = models.CharField(max_length=32, null=True, blank=True)
    count = models.IntegerField(default=0)
    def __str__(self):
        return self.user.username