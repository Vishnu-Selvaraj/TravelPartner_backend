from django.db import models
from django.contrib.auth.models import AbstractUser
from admin_app.models import TourList

import string
import random


# Create your models here.

class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.BigIntegerField(unique=True,null=True)
    password_reset_token = models.CharField(max_length=255,null=True,unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_blocked = models.BooleanField(default=False)

class UserBookings(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    tour = models.ForeignKey(TourList,on_delete=models.CASCADE)
    booking_id = models.CharField(max_length=8, unique=True)
    number_of_persons = models.IntegerField()
    total_price = models.DecimalField(max_digits=10,decimal_places=2)
    trip_start_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
