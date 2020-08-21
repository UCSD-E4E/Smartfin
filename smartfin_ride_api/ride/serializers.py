from rest_framework import serializers

# model we want to serialize, in our models.py file
from .models import Ride

class RideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        # we want to serialize all fields
        fields = '__all__'
