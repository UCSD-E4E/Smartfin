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
import random

# TODO: combine get many with the location and date views


# Create your views here.
@api_view(['GET'])
def rideOverview(request):
    # list of url patterns in this api
    api_urls = {
        'List all ride ids': '/ride-list/',

        'Get single ride': '/ride-get/<str:rideId>/',
        'Get random set of rides': '/many/ride-get/<int:count>/',
        'Filter rides by location': '/location/ride-get/<str:location>/',
        'Filter rides by date': '/date/ride-get/<str:startDate>/<str:endDate>/',

        'Get single ride attribute': 'field-get/<str:rideId>/<str:fields>/',
        'Get attributes of random set of rides': 'random/field-get/<int:count>/<str:fields>/',
        'Get attributes of rides filtered by location': 'location/field-get/<str:location>/<str:fields>/', 
        'Get attributes of rides filtered by date': 'date/field-get/<str:startDate>/<str:endDate>/<str:fields>/',

        'Update heights of all rides in database': 'update-heights/',
        'Get list of active CDIP buoys': 'buoy-list/'
    }

    return Response(api_urls)



# get list of all rideIds
@api_view(['GET'])
def rideList(request):
    rd = RideData.objects.all()
    data = rd.values_list('rideId', flat=True).order_by('startTime')
    data = {'data': data}
    return JsonResponse(data)


# create new ride 
@api_view(['GET'])
def rideGet(request, rideId):
    # if ride already exists in the database, return it
    try: 
        data = RideData.objects.get(rideId=rideId)
        print('found ride in database, returning data...')

    # if ride doesn't exist, then create a new model and fill its data
    except:
        rideModule = RideModule()

        # get all CDIP buoys from db
        buoys = Buoys.objects.values()
        if len(buoys) == 0:
            buoys = rideModule.get_CDIP_stations()
            for buoy in buoys:
                buoyModel = Buoys(**buoy)
                buoyModel.save()
    
        # fetch data from the ride_module
        data = rideModule.get_ride_data(rideId, buoys)
        if data == {}:
            return Response({})

        # save ride data into RideData model
        rideModel = RideData(**data)
        rideModel.save()
        print(f'uploaded {sys.getsizeof(data)} bytes of ride data to database...')

    # return ride data that was sent to model
    serializer = RideSerializer(data, many=False)
    return Response(serializer.data)


@api_view(['GET'])
def rideGetRandom(request, count):

    rideSet = RideData.objects.all()
    if count > 0:
        if count > len(rideSet):
            print('Not enough rides in database')
            return
        rideSet = RideData.objects.all()
        rideSet = random.sample(list(rideSet), count)
    serializer = RideSerializer(rideSet, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def rideGetLocation(request, location):
    # return all ride ids if all locations are specified
    if (location == 'all'):
        rideSet = RideData.objects.all()
    # only return ids in the specified location
    else:
        if ':' in location:
            loc1, loc3 = location.split(':')
        else:
            loc1 = location
            loc3 = location
        # here | is being used as set union not bitwise OR
        rideSet = RideData.objects.filter(Q(loc1=loc1) | Q(loc2=loc1) | Q(loc3=loc1) | Q(loc1=loc3) | Q(loc2=loc3) | Q(loc3=loc3))

    serializer = RideSerializer(rideSet, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def rideGetDate(request, startDate, endDate):
    
    if startDate == 'all':
        rideSet = RideData.objects.all
    try:     
        startDate = int(startDate)
        endDate = int(endDate)
    except:
        return JsonResponse({'error': 'dates must be formatted in unix time'})

    # get all rides that occur after the startDate
    rideSet = RideData.objects.filter(Q(startTime__gte=startDate) & Q(endTime__lte=endDate))
    serializer = RideSerializer(rideSet, many=True)
    return Response(serializer.data)


# get single field from ride
@api_view(['GET']) 
def fieldGet(request, rideId, fields):

    # parse attributes
    attributes = []
    if ':' in fields:
        attributes = fields.split(':')
    else:
        attributes.append(fields)
 
    data = {}
    
    field = RideData.objects.get(rideId=rideId)
    for attribute in attributes:
        data[attribute] = getattr(field, attribute)

    return JsonResponse(data)


# get single field from multiple random rides
@api_view(['GET'])
def fieldGetRandom(request, fields, count):

    # parse attributes 
    if 'rideId' not in fields:
        fields = 'rideId:' + fields
    attributes = []
    if ':' in fields:
        attributes = fields.split(':')
    else:
        attributes.append(fields)

    # build set if ride attributes
    fieldSet = RideData.objects.all().values_list(*attributes)
    if count > 0:
        if count > len(fieldSet):
            print('Not enough rides in database')
            return
        fieldSet = random.sample(list(fieldSet), count)

    # format data to send back
    data = {'data': [dict(zip(attributes, values)) for values in fieldSet]}
    return JsonResponse(data)


@api_view(['GET'])
def fieldGetLocation(request, fields, location):

    # parse attributes
    attributes = []
    if ':' in fields:
        attributes = fields.split(':')

    else:
        attributes.append(fields)

    # return all ride ids if all locations are specified
    if (location == 'all'):
        fieldSet = RideData.objects.all()
        fieldSet = fieldSet.values_list(*attributes)
    # only return ids in the specified location
    else:
        if ':' in location:
            loc1, loc3 = location.split(':')
        else:
            loc1 = location
            loc3 = location
        # here | is being used as set union not bitwise OR
        fieldSet = RideData.objects.filter(Q(loc1=loc1) | Q(loc2=loc1) | Q(loc3=loc1) | Q(loc1=loc3) | Q(loc2=loc3) | Q(loc3=loc3))
        fieldSet = fieldSet.values_list(*attributes)
    
    fieldSet = RideData.objects.all().values_list(*attributes)
    data = {'data': [dict(zip(attributes, values)) for values in fieldSet]}
    return JsonResponse(data)


@api_view(['GET'])
def fieldGetDate(request, startDate, endDate, fields):
    
     # parse attributes
    attributes = []
    if ':' in fields:
        attributes = fields.split(':')

    else:
        attributes.append(fields)

    # parse dates
    try:     
        startDate = int(startDate)
        endDate = int(endDate)
    except:
        return JsonResponse({'error': 'dates must be formatted in unix time'})

    # get all rides that occur after the startDate and before end date
    fieldSet = RideData.objects.filter(Q(startTime__gte=startDate) & Q(endTime__lte=endDate))
    fieldSet = fieldSet.values_list(*attributes)
    data = {'data': [dict(zip(attributes, values)) for values in fieldSet]}
    return JsonResponse(data)





@api_view(['PUT'])
# used to update smartfin calculated heights when new analysis method is used
def updateHeights(request):

    # get all ids currently in database
    ids = RideData.objects.values_list('rideId', flat=True)
    rm = RideModule()

    # for each ride currently in database...
    for id in ids:
        rd = RideData.objects.get(rideId=id)
        mdf = getattr(rd, 'motionData')
        # calculate the new ride height from updated height analysis algorithm
        heightUpdated = rm.get_ride_height(id, mdf)

        # update the old height in the database
        ride = RideData.objects.get(rideId=id)
        ride.heightSmartfin = heightUpdated  # change field
        ride.save() # this will update only

    return JsonResponse({'success': 'rides updated '})



@api_view(['GET'])
def buoyList(request):
    
    # return list of buoys
    data = Buoys.objects.all().values_list('buoyNum', flat=True)
    print(data)
    return Response(data)



# @api_view(['GET'])
# def oceanData(request):

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