from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

#class that extends functionalities of the abstract user which manages information about
# authentication. 
class User(AbstractUser):
    #applying a unique constraint to the email field.
    email = models.EmailField(unique=True)