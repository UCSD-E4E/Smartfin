from django.db import models

# Create your models here.
class RideData(models.Model):

    rideId = models.CharField(max_length=5, primary_key=True) 
    loc1 = models.CharField(max_length=50, blank=True, null=True)
    loc2 = models.CharField(max_length=50, blank=True, null=True)
    loc3 = models.CharField(max_length=50, blank=True, null=True)

    startTime = models.CharField(max_length=20, blank=True, null=True)
    endTime = models.CharField(max_length=20, blank=True, null=True)

    heightSmartfin = models.FloatField(blank=True, null=True)
    heightList = models.TextField(blank=True, null=True)
    heightSampleRate = models.IntegerField(blank=True, null=True)

    tempSmartfin = models.FloatField(blank=True, null=True)
    tempList = models.TextField(blank=True, null=True)
    tempSampleRate = models.IntegerField(blank=True, null=True)

    buoyCDIP = models.CharField(max_length=3)
    heightCDIP = models.FloatField(blank=True, null=True)
    tempCDIP = models.FloatField(blank=True, null=True)

    latitude = models.FloatField(max_length=10, blank=True, null=True)
    longitude = models.FloatField(max_length=10, blank=True, null=True)

    motionData = models.TextField(blank=True, null=True)
    oceanData = models.TextField(blank=True, null=True)

    def __str__(self):
        return 'ride'

    def getHeights(self):
        return {
            'heightSmartfin': self.heightSmartfin,
            'heightCDIP': self.heightCDIP,
            'startTime': self.startTime
        }

    def getTemps(self):
        return {
            'tempSmartfin': self.tempSmartfin,
            'tempCDIP': self.tempCDIP,
            'startTime': self.startTime
        }

    def getMdf(self):
        return {
            'motionData': self.motionData
        }


class Buoys(models.Model):

    buoyNum = models.CharField(max_length=3, primary_key=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return 'buoy'

# class OceanData(models.Model):
#     time = models.FloatField(primary_key=True, default=0)
#     temp1 = models.FloatField(blank=True, null=True)
#     calibratedTemp1 = models.FloatField(blank=True, null=True)
#     temp1Stable = models.FloatField(blank=True, null=True)
#     temp2 = models.FloatField(blank=True, null=True)
#     calibratedTemp2 = models.FloatField(blank=True, null=True)
#     temp2Stable = models.FloatField(blank=True, null=True)
#     rideId = models.CharField(max_length=5, blank=True, null=True) 

#     def __str__(self):
#         return 'ocean'



# class MotionData(models.Model):
#     time = models.FloatField(primary_key=True, default=0)
#     imuA1 = models.FloatField(blank=True, null=True)
#     imuA2 = models.FloatField(blank=True, null=True)
#     imuA3 = models.FloatField(blank=True, null=True)
#     imuG1 = models.FloatField(blank=True, null=True)
#     imuG2 = models.FloatField(blank=True, null=True)
#     imuG3 = models.FloatField(blank=True, null=True)
#     imuM1 = models.FloatField(blank=True, null=True)
#     imuM2 = models.FloatField(blank=True, null=True)
#     imuM3 = models.FloatField(blank=True, null=True)
#     rideId = models.models.ForeignKey("app.Model", on_delete=models.CASCADE)
    
#     def __str__(self):
#         return 'motion'

#     def get_IMU_A2(self):
#         return self.imuA2
        
