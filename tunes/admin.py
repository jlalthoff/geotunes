from django.contrib.gis import admin
from .models import GeoUser
from .models import Playlist
from .models import Tune
from .models import UserTuneLocation
from .models import GeoLocation


class PlaylistAdmin(admin.ModelAdmin):
    readonly_fields = ['date_created']
    list_filter = ('owner', 'name')


class UserTuneLocationInline(admin.TabularInline):
    model = UserTuneLocation


class GeoLocationAdmin(admin.OSMGeoAdmin):
    ordering = ['state', 'name']
    search_fields = ['name']
    readonly_fields = ['area']
    list_filter = ('type', 'name', 'state')
    inlines = [UserTuneLocationInline]


class UserTuneLocationAdmin(admin.ModelAdmin):
    list_fiter = ['name']


class TuneAdmin(admin.ModelAdmin):
    readonly_fields = ["time_last_played", "time_last_skipped", "play_count", "skip_count"]
    list_filter = ('owner', 'title', 'author')


admin.site.register(Playlist, PlaylistAdmin)
admin.site.register(Tune, TuneAdmin)
admin.site.register(GeoLocation, GeoLocationAdmin)

admin.site.register(GeoUser, admin.OSMGeoAdmin)
admin.site.register(UserTuneLocation, UserTuneLocationAdmin)
