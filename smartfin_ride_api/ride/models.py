from django.db import models

# Create your models here.
class Ride(models.Model):

    ride_id = models.CharField(max_length=5, primary_key=True) 
    start_time = models.CharField(max_length=20, blank=True, null=True)
    end_time = models.CharField(max_length=20, blank=True, null=True)
    CDIP_buoy = models.CharField(max_length=3)
    CDIP_height = models.FloatField(blank=True, null=True)
    CDIP_temp = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(max_length=10, blank=True, null=True)
    longitude = models.FloatField(max_length=10, blank=True, null=True)
    

    def __str__(self):
        return ride_id

# class Ocean_Data(models.Model):


# class Motion_Data(models.Model):
#     imuA1 = models.FloatField(blank=True, null=True)
#     imuA2 = models.FloatField(blank=True, null=True)
#     imuA3 = models.FloatField(blank=True, null=True)
#     time = models.IntegerField(blank=True, null=True)
#     ride_id = models.CharField(