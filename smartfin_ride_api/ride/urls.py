"""smartfin_ride_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views


urlpatterns = [
    path('', views.rideOverview, name='ride-overview'),

    path('ride-list/', views.rideList, name='ride-list'),

    path('ride-get/<str:rideId>/', views.rideGet, name='ride-get-single'),
    path('random/ride-get/<int:count>/', views.rideGetRandom, name='ride-get-random'),
    path('location/ride-get/<str:location>/', views.rideGetLocation, name='ride-get-location'),
    path('date/ride-get/<str:startDate>/<str:endDate>/', views.rideGetDate, name='ride-get-date'),

    path('field-get/<str:rideId>/<str:fields>/', views.fieldGet, name='field-get'),
    path('random/field-get/<int:count>/<str:fields>/', views.fieldGetRandom, name='field-get-random'),
    path('location/field-get/<str:location>/<str:fields>/', views.fieldGetLocation, name='field-get-location'),
    path('date/field-get/<str:startDate>/<str:endDate>/<str:fields>/', views.fieldGetDate, name='field-get-date'),

    path('update-heights/', views.updateHeights, name='update-heights'),
   
    path('buoy-list/', views.buoyList, name='buoy-list'),
]
