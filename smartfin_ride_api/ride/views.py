from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

from rest_framework.response import Response
from rest_framework.decorators import api_view

from .serializers import RideSerializer, HeightSerializer, TempSerializer
import sys 
sys.path.append('../')
from smartfin_ride_module import RideModule
from .models import RideData #, OceanData, MotionData


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
        data = rideModule.get_ride_data(rideId)

        # save ride data into RideData model
        rideModel = RideData(**data)
        rideModel.save()
        print(f'uploaded {sys.getsizeof(data)} bytes of ride data to database...')

    # return ride data that was sent to model
    serializer = RideSerializer(data, many=False)
    return Response(serializer.data)


@api_view(['GET']) 
def heightList(request):
    heights = RideData.objects.values_list('heightSmartfin', 'heightCDIP')
    data = {'heightSmartfin': heights[0], 'heightCDIP': heights[1]}
    return JsonResponse(data)


@api_view(['GET'])
def tempList(request):
    temps = RideData.objects.values_list('tempSmartfin', 'tempCDIP')
    data = {'tempSmartfin': temps[0], 'tempCDIP': temps[1]}
    return JsonResponse(data)


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

   