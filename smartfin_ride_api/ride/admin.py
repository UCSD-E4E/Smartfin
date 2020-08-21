from django.contrib import admin
from .models import Ride

# Register your models here.
# class TaskAdmin(admin.ModelAdmin):
#     readonly_fields = ('id',)

# Register your models here.
admin.site.register(Ride)