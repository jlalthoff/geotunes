from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.gis.forms import OSMWidget, MultiPolygonField, ModelForm, CharField, TypedChoiceField, \
    PointField
from django.forms import FileField, FilePathField, Form

from .models import GeoLocation, GeoUser, MusicLibrary, Playlist
from .models import State, Tune


#  sample form with vaildation:
#  from django.core.exceptions import ValidationError
#  from django.utils.translation import ugettext_lazy as _
#
# class RenewBookForm(forms.Form):
#     renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks (default 3).")
#
#     def clean_renewal_date(self):
#         data = self.cleaned_data['renewal_date']
#
#         # Check if a date is not in the past.
#         if data < datetime.date.today():
#             raise ValidationError(_('Invalid date - renewal in past'))
#
#         # Check if a date is in the allowed range (+4 weeks from today).
#         if data > datetime.date.today() + datetime.timedelta(weeks=4):
#             raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))
#
#         # Remember to always return the cleaned data.
#         return data


class RegisterMusicForm(Form):
    name = forms.CharField()
    directory = FilePathField(path='/', required=False,
                              widget=forms.ClearableFileInput(attrs=
                                                               {'multiple': True}),
                              )

    # class Meta:
    #     model = Playlist
    #     fields = ['name', 'directory']


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


# used for "Tunes"  (search)menu choice
class TuneSearchForm(ModelForm):
    artist = CharField(required=False)
    title = CharField(required=False)
    album = CharField(required=False)

    class Meta:
        model = Tune
        fields = ['artist', 'title', 'album']


# class TuneUploadForm(ModelForm):
#     tune_content = FileField(required=True)
#     playlist = CharField(required=True)
#
#     class Meta:
#         model = Tune
#         fields = ['tune_content']

class TuneUploadForm(Form):
    tune_content = FileField(required=True, help_text='Choose one or more. Only new songs will be saved',
                             widget=forms.ClearableFileInput(attrs=
                                                               {'multiple': True}))
    playlist = CharField(required=True, help_text='select a new or existing playlist')