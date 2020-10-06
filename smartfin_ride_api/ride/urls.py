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
    path('many/ride-get/<int:count>/', views.rideGetMany, name='ride-get-many'),

    path('field-get/<str:rideId>/<str:fields>/', views.fieldGet, name='field-get'),
    path('many/field-get/<str:fields>/<int:count>/', views.fieldGetMany, name='field-get-many'),

    path('ride-locate/<str:location>/', views.rideFindByLoc, name='ride-locate'),

    path('ride-date/<str:startDate>/<str:endDate>/', views.rideFindByDate, name='ride-date'),

    path('update-heights/', views.updateHeights, name='update-heights'),
    path('motion-data/<str:rideId>/', views.motionData, name='motion-data'),
    # path('ocean-list/', views.oceanList, name='ocean-list'),
    # path('motion-detail/<str:rideId>/', views.motionDetail, name='motion-detail'),\
    path('buoy-list/', views.buoyList, name='buoy-list'),
    # path('ocean-detail/<str:rideId>/', views.oceanDetail, name='ocean-detail')
]
