from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from rest_framework import serializers

from rest_framework.response import Response
from rest_framework.decorators import api_view

from .serializers import RideSerializer, HeightSerializer, TempSerializer, BuoySerializer
import sys 
sys.path.append('../')
from smartfin_ride_module import RideModule
from .models import RideData, Buoys
import json


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


# get list of all rides
@api_view(['GET'])
def rideList(request):

    data = RideData.objects.all()
    serializer = RideSerializer(data, many=True)
    return Response(serializer.data)


# get detailed info of specific ride
@api_view(['GET'])
def rideDetail(request, rideId):
    data = RideData.objects.get(rideId=rideId)
    serializer = RideSerializer(data, many=False)
    return Response(serializer.data)


# create new ride 
@api_view(['GET'])
def rideCreate(request, rideId):

    try: 
        data = RideData.objects.get(rideId=rideId)
        print('found ride in database, returning data...')

    except:

         # fetch data from ride id
        rideModule = RideModule()

        buoys = Buoys.objects.values()

        if len(buoys) == 0:
            buoys = rideModule.get_CDIP_stations()
            for buoy in buoys:
                buoyModel = Buoys(**buoy)
                buoyModel.save()
    
        data = rideModule.get_ride_data(rideId, buoys)

        # save ride data into RideData model
        rideModel = RideData(**data)
        rideModel.save()
        print(f'uploaded {sys.getsizeof(data)} bytes of ride data to database...')

    # return ride data that was sent to model
    serializer = RideSerializer(data, many=False)
    return Response(serializer.data)


@api_view(['GET']) 
def heightList(request, location):
    if (location == 'all'):
        rd = RideData.objects.all()
    else:
        loc1, loc3 = location.split(':')
        # here | is being used as set union not bitwise OR
        rd = RideData.objects.filter(Q(loc1=loc1) | Q(loc2=loc1) | Q(loc3=loc1) | Q(loc1=loc3) | Q(loc2=loc3) | Q(loc3=loc3) )

    r = rd.values_list('rideId', flat=True).order_by('startTime')
    s = rd.values_list('heightSmartfin', flat=True).order_by('startTime')
    c = rd.values_list('heightCDIP', flat=True).order_by('startTime')
    t = rd.values_list('startTime', flat=True).order_by('startTime')

    data = {'rideId': list(r), 'heightSmartfin': list(s), 'heightCDIP': list(c), 'startTime': list(t)}
    return JsonResponse(data)


@api_view(['GET'])
def tempList(request, location):
    if (location == 'all'):
        rd = RideData.objects.all()
    else:
        loc1, loc3 = location.split(':')
        # here | is being used as set union not bitwise OR
        rd = RideData.objects.filter(Q(loc1=loc1) | Q(loc2=loc1) | Q(loc3=loc1) | Q(loc1=loc3) | Q(loc2=loc3) | Q(loc3=loc3) )

    r = rd.values_list('rideId', flat=True).order_by('startTime')
    s = rd.values_list('tempSmartfin', flat=True).order_by('startTime')
    c = rd.values_list('tempCDIP', flat=True).order_by('startTime')
    t = rd.values_list('startTime', flat=True).order_by('startTime')

    data = {'rideId': list(r), 'tempSmartfin': list(s), 'tempCDIP': list(c), 'startTime': list(t)}
    return JsonResponse(data)

# used to update smartfin calculated heights when new analysis method is used
def updateHeights(request):
    ids = RideData.objects.values_list('rideId', flat=True)
    rm = RideModule()

    for id in ids:
        heightUpdated = rm.get_ride_height(id)
        ride = RideData.objects.get(rideId=id)
        ride.heightSmartfin = heightUpdated  # change field
        ride.save() # this will update only

    return JsonResponse({})


# @api_view(['GET'])
# def motionList(request):

#     data = MotionData.objects.all()
#     serializer = MotionSerializer(data, many=True)
#     return Response(serializer.data)


# @api_view(['GET'])
# def oceanList(request):

#     data = OceanData.objects.all()
#     serializer = OceanSerializer(data, many=True)
#     return Response(serializer.data)


# @api_view(['GET'])
# def motionDetail(request, rideId):

#     data = MotionData.objects.filter(rideId=rideId)
#     serializer = MotionSerializer(data, many=True)
#     return Response(serializer.data)


# @api_view(['GET'])
# def oceanDetail(request, rideId):

#     data = OceanData.objects.filter(rideId=rideId)
#     serializer = OceanSerializer(data, many=True)
#     return Response(serializer.data)

   