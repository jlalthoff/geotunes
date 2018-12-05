from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .Library import Library
from .forms import LibraryLoadForm
from .forms import UserForm, UserLocationForm, GeoLocationForm, GeoUserForm
from .models import MusicLibrary, MusicLibraryPlaylist
from .models import Playlist, Tune, GeoUser, UserTuneLocation, GeoLocation


# ------------------------------------------------------------

def index(request):
    context = {}
    return render(request, 'index.html', context=context)


# ------------------------------------------------------------

class TuneCreate(LoginRequiredMixin, CreateView):
    model = Tune
    fields = ['tune_content', 'title', 'artist']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class TuneDelete(LoginRequiredMixin, DeleteView):
    model = Tune
    fields = ['title', 'artist', 'usertunelocations']
    success_url = reverse_lazy('tunes')


# class TuneDetailView(LoginRequiredMixin, DetailView):
#     model = Tune


class TuneListView(LoginRequiredMixin, ListView):
    model = Tune
    paginate_by = 25

    def get_queryset(self):
        return Tune.objects.filter(owner=self.request.user.id)


# ------------------------------------------------------------
class GeoLocationList(LoginRequiredMixin, ListView):
    model = GeoLocation
    paginate_by = 20

    def get(self, request):
        if 'name' in request.GET:
            form = GeoLocationForm(request.GET)
            if form.is_valid():
                search_param = form.cleaned_data.get('name')
                locations = GeoLocation.objects.filter(name__icontains=search_param)
                if 'state' in request.GET:
                    state_search = form.cleaned_data.get('state')
                    if state_search:
                        locations = locations.filter(state=form.cleaned_data.get('state'))
                return render(request, 'tunes/geolocation_list.html', {'location_list': locations})
        else:
            form = GeoLocationForm()
        return render(request, 'tunes/geolocation_search.html', {'form': form})


class MyGeoLocationList(LoginRequiredMixin, ListView):
    model = GeoLocation
    paginate_by = 20

    def get(self, request):
        if 'name' in request.GET:
            form = GeoLocationForm(request.GET)
            if form.is_valid():
                user = self.request.user
                search_param = form.cleaned_data.get('name')
                locations = GeoLocation.objects.filter(owner=user).filter(name__icontains=search_param)
                if 'state' in request.GET:
                    state_search = form.cleaned_data.get('state')
                    if state_search:
                        locations = locations.filter(state=form.cleaned_data.get('state'))
                return render(request, 'tunes/geolocation_list.html', {'location_list': locations})
        else:
            form = GeoLocationForm()
        return render(request, 'tunes/geolocation_search.html', {'form': form})

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


# class GeoLocationDetail(LoginRequiredMixin, DetailView):
#     model = GeoLocation
#     form_class = UserLocationForm
#     fields ={'name', 'type', 'state', 'geom'}
#     template_name = 'tunes/geolocation_detail.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         tune_list = findsongsbyarea(self.object)
#         context['tune_list'] = tune_list
#         print(context)
#         return context
#
#         def get_success_url(self):
#             return reverse('geolocation_detail',
#                            kwargs={'pk': self.object.pk})


def findsongsbyarea(thelocation):
    # use these given area to find the corresponding user-tune-locations
    utl_list = UserTuneLocation.objects.filter(location=thelocation)
    # then use the user tune locations to get the related tunes.
    the_tunes = Tune.objects.filter(usertunelocation__in=utl_list)
    return the_tunes


class GeoLocationCreate(LoginRequiredMixin, CreateView):
    form_class = UserLocationForm
    template_name = 'tunes/geolocation_create.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class GeoLocationUpdate(LoginRequiredMixin, UpdateView):
    model = GeoLocation
    template_name = 'tunes/geolocation_detail.html'
    form_class = UserLocationForm

    def get_success_url(self):
        return reverse('geolocation_update',
                       kwargs={'pk': self.object.pk})


# ------------------------------------------------------------
@login_required
def song(request, pk):
    thesong = get_object_or_404(Tune, pk=pk)
    geolocation_list = []
    u = get_object_or_404(User, pk=request.user.pk)
    playlists = Playlist.objects.filter(owner=u)
    button = 'Search'
    if request.method == 'POST':
        searchparam = request.POST['query']
        if searchparam:
            button = 'Add selected locations:'
            geolocation_list = GeoLocation.objects.filter(name__icontains=searchparam)
        else:
            addlocations(request.POST.getlist('geoloc'), thesong)
    context = {'song': thesong, 'locations': geolocation_list,
               'button_title': button, 'playlist_list': playlists,
               }
    return render(request, 'tunes/song_detail.html', context=context)


def addlocations(loclist, thesong):
    for loc in loclist:
        utl = UserTuneLocation()
        utl.user = get_object_or_404(User, pk=thesong.owner.id)
        utl.location = get_object_or_404(GeoLocation, pk=loc)
        utl.tune = thesong
        utl.save()


# -------------------------------------------------------------


# @login_required
# def loadlibrary(request):
#     song_count = Tune.objects.all().count()
#     library_list = MusicLibrary.objects.all()
#     context = {
#         'song_count': song_count,
#         'library_list': library_list,
#     }
#     if request.method == 'POST':
#         form = LibraryLoadForm(request.POST)
#         context['form'] = form
#         # if form.is_valid():
#         # print(form.cleaned_data)
#         # libloc = form.cleaned_data['name']
#         # process the data in form.cleaned_data
#
#         load_count = 0;
#         return render(request, 'tunes/playlist_load.html', context)
#     else:
#         form = LibraryLoadForm()
#
#         return render(request, 'tunes/playlist_load.html', context)


# -------------------------------------------------------------

class GeoUserUpdate(LoginRequiredMixin, UpdateView):
    form_class = GeoUserForm
    model = GeoUser
    template_name = 'tunes/geouser_form.html'

    def get_success_url(self):
        return reverse('geouser_update',
                       kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tune_list = findsongs(self.object)
        context['tune_list'] = tune_list
        return context


def findsongs(theuser):
    # get the smallest areas first so we get tunes for the most-specific location.
    areas = GeoLocation.objects.filter(geom__contains=theuser.default_center_point).order_by('area')
    # use these areas to find the corresponding user-tune-locations
    utl_list = UserTuneLocation.objects.filter(location__in=areas)
    # then use the user tune locations to get the related tunes.
    the_tunes = Tune.objects.filter(usertunelocation__in=utl_list)
    return the_tunes


# ------------------------------------------------------------

class PlaylistListView(LoginRequiredMixin, ListView):
    model = Playlist
    paginate_by = 25

    def get_queryset(self):
        return Playlist.objects.filter(owner=self.request.user.id)


class PlaylistDetail(LoginRequiredMixin, DetailView):
    model = Playlist


class PlaylistPlay(LoginRequiredMixin, DetailView):
    model = Playlist
    template_name = 'tunes/playlist_play.html'


class PlaylistCreate(LoginRequiredMixin, CreateView):
    model = Playlist
    fields = ['name', 'tunes']

    def form_valid(self, form):
        u = User.objects.get(pk=self.request.user.pk)
        form.instance.owner = u
        return super().form_valid(form)


class PlaylistUpdate(LoginRequiredMixin, UpdateView):
    model = Playlist
    fields = ['name', 'tunes']


class PlaylistDelete(LoginRequiredMixin, DeleteView):
    model = Playlist
    success_url = reverse_lazy('playlists')


# ------------------------------------------------------------

class UserTuneLocationDelete(LoginRequiredMixin, DeleteView):
    model = UserTuneLocation

    def get_success_url(self):
        return reverse('tune_detail',
                       kwargs={'pk': self.object.tune.pk})


class LinkCreate(LoginRequiredMixin, CreateView):
    model = UserTuneLocation
    fields = ['tune', 'location']

    def form_valid(self, form):
        key = self.request.user.pk
        u = get_object_or_404(User, pk=key)
        form.instance.user = u
        return super().form_valid(form)


# ------------------------------------------------------------

@transaction.atomic
def register(request):
    """
    register a new user for the system.
    :param request:
    :return:
    """
    if request.method == 'POST':
        f = UserForm(request.POST)
        if f.is_valid():
            f.save()
            messages.success(request, 'Account created successfully')
            return render(request, 'index.html')
    else:
        f = UserForm()
    return render(request, 'tunes/register.html', {'user_form': f})


class UserUpdate(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'tunes/user_form.html'
    success_url = reverse_lazy('index')
    fields = ['username', 'first_name', 'last_name', 'email']


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.warning(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'tunes/change_password.html', {
        'form': form
    })


# ------------------------------------------------------------

class LoadLibrary(LoginRequiredMixin, CreateView):
    form_class = LibraryLoadForm
    model = Playlist

    # def form_valid(self, form):
    #     print(form.cleaned_data['name'])
    #     lib = get_object_or_404(MusicLibrary, name=form.cleaned_data['lib_name'])
    #     # does playlist already exist?
    #     print('library found:', lib)
    #     # add new songs to database, add each song to the Playlist (form.instance)
    #     g = GeoUser.objects.get(pk=self.request.user.pk)
    #     form.instance = addLibrarySongs(lib, form.instance, g)
    #     form.instance.owner = g
    #     try:
    #         return super().form_valid(form)
    #     except IntegrityError as e:
    #         messages.add_message(self.request, messages.ERROR,
    #                              'You already loaded this playlist')
    #         return render(self.request, template_name='tunes/playlist_list.html',
    #                       context=self.get_context_data())


def addLibrarySongs(lib, playlist, geoowner):
    print('Using:', lib.filepath, ' with ', playlist.name)
    l = Library.Library(lib.filepath)
    pl = l.getPlaylist(playlist.name)
    owner = geoowner.user
    if pl:
        for song in pl.tracks:
            print(song.location, '======', song.name, ' BY ', song.artist)
            try:
                t = Tune.objects.get(tune_url=song.location_escaped)
            except Tune.DoesNotExist:
                t = Tune()
                t.owner = owner
                t.artist = song.artist
                t.title = song.name
                t.album = song.album
                t.tune_content = song.location
                t.tune_url = song.location_escaped
                t.save(commit=False)
                print('Saved', t)
            # just add "t" object to the list of songs for the new_playlist
            playlist.tunes.append(t)
    else:
        print('playlist does not exist in library specified.')
    return playlist


class LibCreate(LoginRequiredMixin, CreateView):
    model = MusicLibrary
    fields = ['name', 'type', 'filepath']

    def form_valid(self, form):
        # add a MusicLibraryPlaylist for each playlist found in the MusicLibrary.
        # form.instance = addLibraryPlaylists(form.instance)
        form.instance.save()
        lib = Library(form.instance.filepath)
        for plname in lib.getPlaylistNames():
            p = MusicLibraryPlaylist(library=form.instance)
            p.name = plname
            p.loaded = False
            p.save()
        return super().form_valid(form)


class LibraryDetail(LoginRequiredMixin, DetailView):
    model = MusicLibrary
    fields = ['name', 'type', 'filepath']


class LibPlaylistLoad(LoginRequiredMixin, UpdateView):
    model = MusicLibraryPlaylist
    fields = ('name', 'loaded',)
    pk_url_kwarg = 'playlist_pk'
    context_object_name = 'playlist'


    def songs(self):
        lib = Library(playlist.library.filepath)
        songs = lib.getPlaylist(playlist.name)
        return songs

@login_required
def libplaylistload(request, pk):
    thepl = get_object_or_404(MusicLibraryPlaylist, pk=pk)
    lib = Library(thepl.library.filepath)
    song_list = lib.getPlaylist(thepl.name).tracks
    context = {'library': thepl.library.name, 'song_list': song_list, 'name': thepl.name, }
    if request.method == 'POST':
        key = request.user.pk
        owner = get_object_or_404(User, pk=key)
        playlist = Playlist()
        playlist.name = thepl.name
        playlist.owner = owner
        playlist.save()
        for song in song_list:
            savesong(song, owner, playlist)
    return render(request, 'tunes/musiclibraryplaylist_form.html', context=context)

def savesong(song, o, playlist):
    t = Tune()
    try:
        t.owner = o
        t.artist = song.artist
        t.title = song.name
        t.album = song.album
        t.tune_content = song.location
        t.tune_url = song.location_escaped
        t.save()
    except:
        pass
    playlist.tunes.add(t)
    playlist.save()
