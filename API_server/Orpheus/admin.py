from django.contrib import admin
from .models import Player, Schedule, MainStream, Inserts, Silent, PlayerStatus, UpdateFile

class UpdateFileAdmin(admin.ModelAdmin):
    list_display = ['file_type', 'version', 'url']

class PlayerStatusInline(admin.TabularInline):
    model = PlayerStatus
    fields = ('player_version', 'status', 'timestamp', 'current_sch_time', 'updater_present')
    readonly_fields = ('player_version', 'status', 'timestamp', 'current_sch_time', 'updater_present')

class PlayerAdmin(admin.ModelAdmin):
    list_display = ['player_id', 'address', 'title', 'schedule', 'update_granted', 'stat']
    inlines = [PlayerStatusInline,]
    actions = ['update_grant', 'update_deny']

    def update_grant(self, request, queryset):
        queryset.update(update_granted=True)
    update_grant.short_description = "Разрешить обновление"

    def update_deny(self, request, queryset):
        queryset.update(update_granted=False)
    update_deny.short_description = "Запретить обновление"


class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['title', 'change_time', 'main_stream', 'get_inserts_count', 'get_silent_count']
    filter_horizontal = ('inserts', 'silent')


class MainStreamAdmin(admin.ModelAdmin):
    list_display = ['description', 'url']


class InsertAdmin(admin.ModelAdmin):
    list_display = ['description', 'url', 'time']


class SilentAdmin(admin.ModelAdmin):
    list_display = ['description', 'time_start', 'time_end']

admin.site.register(UpdateFile, UpdateFileAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(MainStream, MainStreamAdmin)
admin.site.register(Inserts, InsertAdmin)
admin.site.register(Silent, SilentAdmin)