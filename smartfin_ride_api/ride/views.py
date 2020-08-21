from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

from rest_framework.response import Response
from rest_framework.decorators import api_view

from .serializers import RideSerializer
import sys 
sys.path.append('../')
from smartfin_ride_module import Ride


# Create your views here.
    
@api_view(['GET'])
def rideOverview(request):

    # list of url patterns in this api
    api_urls = {
        # list of all tasks
        'List': '/ride-list/',
        # detailed view of one task
        'Detail View': '/ride-detail/<str:pk>/',
        # create update and delete functions
        'Create' : '/ride-create/',
        'Update' : '/ride-update/<str:pk>/',
        'Delete' : '/ride-delete/<stk:pk>/',
    }

    return Response(api_urls)

       
@api_view(['GET'])
def rideCreate(request, ride_id):

    print(ride_id)
    ride = Ride()
    data = ride.get_ride_data(ride_id)
    # serializer = RideSerializer(data)

    # if serializer.is_valid():
    #     print('swagitworks')
    #     serializer.save()
    # else:
    #     print('nah')

    return Response(data)