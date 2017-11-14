from django.contrib import admin
from .models import Location, Schedule, MainStream, Inserts, Silent


class LocationAdmin(admin.ModelAdmin):
    list_display = ['title', 'address', 'schedule']


class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['title', 'change_time', 'main_stream', 'get_inserts_count', 'get_silent_count']


class MainStreamAdmin(admin.ModelAdmin):
    list_display = ['description', 'url']


class InsertAdmin(admin.ModelAdmin):
    list_display = ['description', 'url', 'time']


class SilentAdmin(admin.ModelAdmin):
    list_display = ['description', 'time_start', 'time_end']



admin.site.register(Location, LocationAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(MainStream, MainStreamAdmin)
admin.site.register(Inserts, InsertAdmin)
admin.site.register(Silent, SilentAdmin)