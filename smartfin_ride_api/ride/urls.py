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
    path('ride-create/<str:rideId>/', views.rideCreate, name='ride-create'),
    path('height-list/<str:location>/', views.heightList, name='height-list'),
    path('temp-list/<str:location>/', views.tempList, name='temp-list'),
    path('update-heights/', views.updateHeights, name='update-heights'),
    path('motion-data/<str:rideId>/', views.motionData, name='motion-data'),
    # path('ocean-list/', views.oceanList, name='ocean-list'),
    path('ride-detail/<str:rideId>/', views.rideDetail, name='ride-detail'),
    # path('motion-detail/<str:rideId>/', views.motionDetail, name='motion-detail'),\
    path('buoy-list/', views.buoyList, name='buoy-list'),
    # path('ocean-detail/<str:rideId>/', views.oceanDetail, name='ocean-detail')
]
