from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.gis.forms import OSMWidget, MultiPolygonField, ModelForm, CharField, TypedChoiceField, \
    PointField

from .models import GeoLocation, GeoUser,  MusicLibrary, Playlist
from .models import State


class UserForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')


# there is probably a more elegant way for state_list, allowing no state to be
# picked, but I couldn't find one
state_list = State.objects.all().order_by('code').values_list('code', 'name')
pick_list = []
pick_list.append((None, '-------'))
for s in state_list:
    pick_list.append(s)


# used for "Locations"  (search)menu choice
class GeoLocationForm(ModelForm):
    name = CharField(required=True)
    state = TypedChoiceField(choices=pick_list, required=False)

    class Meta:
        model = GeoLocation
        fields = ['name', 'state', ]


# used for the "Add Location" menu choice
class UserLocationForm(ModelForm):
    name = CharField(required=True)
    state = TypedChoiceField(choices=list(pick_list), required=False)
    geom = MultiPolygonField(label='Location',
                             widget=OSMWidget(
                                 attrs={'default_lat': 39.632504, 'default_lon': -84.197948,
                                        'default_zoom': 12,
                                        'template_name': 'gis/openlayers-osm.html',
                                        })
                             )

    class Meta:
        model = GeoLocation
        fields = ['geom', 'name', 'state']


# used for geolocation details
# class GeoLocationUpdateForm(ModelForm):
#     name = CharField(required=True)
#     state = TypedChoiceField(choices=list(pick_list), required=False)
#     geom = MultiPolygonField(label='Location', srid=4326,
#                              widget=OSMWidget(
#                                  attrs={'default_lat': 39.632504, 'default_lon': -84.197948,
#                                         'default_zoom': 12,
#                                         'template_name': 'gis/openlayers-osm.html',
#                                         }))
#
#     class Meta:
#         model = GeoLocation
#         fields = ['name', 'state', 'type',  'geom']


# used for the "Set My Location" menu choice
class GeoUserForm(ModelForm):
    default_center_point = PointField(label='Click a point for your location',
                                      widget=OSMWidget(
                                          attrs={'default_lat': 40, 'default_lon': -84, 'default_zoom': 12,
                                                 'template_name': 'gis/openlayers-osm.html',
                                                 }
                                      ))

    class Meta:
        model = GeoUser
        fields = ['default_center_point']


class LibraryLoadForm(ModelForm):
    lib_name = forms.ModelChoiceField(queryset=MusicLibrary.objects.all(),
                                  label='Choose a library',
                                  help_text='Choose a previously defined library')
    name = forms.CharField(label='Playlist name',
                               initial='----------')

    class Meta:
        model = Playlist
        fields = ['name']
