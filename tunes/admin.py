from django.contrib.gis import admin

from .models import GeoLocation
from .models import GeoUser
from .models import MusicLibrary
from .models import MusicLibraryPlaylist
from .models import Playlist
from .models import Tune
from .models import UserTuneLocation


class MusicLibraryAdmin(admin.ModelAdmin):
    pass


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
    list_filter = ('owner', 'title', 'artist', 'album')


class MusicLibraryPlaylistAdmin(admin.ModelAdmin):
    pass


admin.site.register(MusicLibraryPlaylist, MusicLibraryPlaylistAdmin)
admin.site.register(MusicLibrary, MusicLibraryAdmin)
admin.site.register(Playlist, PlaylistAdmin)
admin.site.register(Tune, TuneAdmin)
admin.site.register(GeoLocation, GeoLocationAdmin)

admin.site.register(GeoUser, admin.OSMGeoAdmin)
admin.site.register(UserTuneLocation, UserTuneLocationAdmin)
