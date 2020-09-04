from django.contrib import admin
from .models import RideData, Buoys

# Register your models here.
class TaskAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)

# Register your models here.
admin.site.register(RideData)
admin.site.register(Buoys)
# admin.site.register(OceanData)
# admin.site.register(MotionData)