from django.db import models
import datetime

# Create your models here.


class TourList(models.Model):
    place_name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10,decimal_places=2)
    image = models.FileField(upload_to='uploads/images')
    total_trip_days = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add= True)

class Itinerary(models.Model):
    tour = models.ForeignKey(TourList,on_delete=models.CASCADE)
    day = models.PositiveIntegerField()
    activities = models.TextField()