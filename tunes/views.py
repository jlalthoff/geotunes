from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import transaction
from django.db.utils import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.list import MultipleObjectMixin
from tinytag import TinyTag, TinyTagException

from .Library import Library
from .filters import TuneFilter
from .forms import TuneSearchForm, TuneUploadForm
from .forms import UserForm, UserLocationForm, GeoLocationForm, GeoUserForm
from .models import MusicLibrary, MusicLibraryPlaylist
from .models import Playlist, Tune, GeoUser, UserTuneLocation, GeoLocation


#
# @login_required
# def renew_book_librarian(request, pk):
#     book_instance = get_object_or_404(BookInstance, pk=pk)
#
#     # If this is a POST request then process the Form data
#     if request.method == 'POST':
#
#         # Create a form instance and populate it with data from the request (binding):
#         form = RenewBookForm(request.POST)
#
#         # Check if the form is valid:
#         if form.is_valid():
#             # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
#             book_instance.due_back = form.cleaned_data['renewal_date']
#             book_instance.save()
#
#             # redirect to a new URL:
#             return HttpResponseRedirect(reverse('all-borrowed') )
# alternatively
#             return redirect('board_topics', pk=board.pk)
#
#     # If this is a GET (or any other method) create the default form.
#     else:
#         proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
#         form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})
#
#     context = {
#         'form': form,
#         'book_instance': book_instance,
#     }
#
#     return render(request, 'catalog/book_renew_librarian.html', context)


# ------------------------------------------------------------

def index(request):
    context = {}
    return render(request, 'index.html', context=context)


# ------------------------------------------------------------

class TuneCreate(LoginRequiredMixin, FormView):
    form_class = TuneUploadForm
    template_name = 'tunes/tune_form.html'
    success_url = reverse_lazy('tune_create')

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('tune_content')
        if form.is_valid():
            name = form.cleaned_data['playlist']
            user = get_object_or_404(User, pk=request.user.pk)
            playlist = Playlist()
            playlist.name = name
            playlist.owner = user
            try:
                playlist.save()
            except IntegrityError:
                # already exists, go and get the original one
                playlist = get_object_or_404(Playlist, name=name, owner=user)
            for f in files:
                add_to_playlist(playlist, f)
            return HttpResponseRedirect(playlist.get_absolute_url())
        else:
            return self.form_invalid(form)


def add_to_playlist(playlist, file):
    t = Tune()
    t.tune_content = file
    t.artist = 'temp999'
    t.album = 'temp999'
    t.title = 'temp999'
    t.owner = playlist.owner
    # must save at this point to get the absolute path so we can scan for meta tags
    t.save()
    try:
        tag = TinyTag.get(t.tune_content.path)
        t.artist = tag.artist
        t.title = tag.title
        t.album = tag.album
    except TinyTagException:
        # TODO: add this as error to messages.
        t.delete()
        return
    try:
        t.save()
    except IntegrityError:
        # fails because title/artist/album already in db.
        # TODO add this as warning to messages.
        t.delete()
        return
    # add to the playlist
    playlist.tunes.add(t)
    playlist.save()
    return


class TuneDelete(LoginRequiredMixin, DeleteView):
    model = Tune
    fields = ['title', 'artist', 'usertunelocations']
    success_url = reverse_lazy('tune_search')


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
                return render(request, 'tunes/geolocation_search.html', {'location_list': locations, 'form': form})
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
                return render(request, 'tunes/geolocation_search.html', {'location_list': locations, 'form': form})
        else:
            form = GeoLocationForm()
        return render(request, 'tunes/geolocation_search.html', {'form': form})

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


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
    is_m4p = str(thesong.tune_content).endswith('.m4p')
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
               'is_m4p': is_m4p
               }
    return render(request, 'tunes/tune_detail.html', context=context)


def addlocations(loclist, thesong):
    for loc in loclist:
        utl = UserTuneLocation()
        utl.user = get_object_or_404(User, pk=thesong.owner.id)
        utl.location = get_object_or_404(GeoLocation, pk=loc)
        utl.tune = thesong
        utl.save()


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


class PlaylistDetail(LoginRequiredMixin, DetailView, MultipleObjectMixin):
    model = Playlist
    paginate_by = 25

    def get_context_data(self, **kwargs):
        playlist = self.get_object()
        object_list = playlist.tunes.all()
        context = super(PlaylistDetail, self).get_context_data(object_list=object_list, **kwargs)
        return context


class PlaylistPlay(LoginRequiredMixin, DetailView):
    model = Playlist
    template_name = 'tunes/playlist_play.html'


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


class LibCreate(LoginRequiredMixin, CreateView):
    model = MusicLibrary
    fields = ['name', 'type', 'filepath']

    def form_valid(self, form):
        # add a MusicLibraryPlaylist for each playlist found in the MusicLibrary.
        key = self.request.user.pk
        u = get_object_or_404(User, pk=key)
        form.instance.owner = u
        form.instance.save()
        lib = Library(form.instance.filepath)
        for plname in lib.getPlaylistNames():
            p = MusicLibraryPlaylist(library=form.instance)
            p.name = plname
            p.loaded = False
            p.save()
        return super().form_valid(form)


class LibraryList(LoginRequiredMixin, ListView):
    model = MusicLibrary
    paginate_by = 25

    def get_queryset(self):
        return MusicLibrary.objects.all()


class LibraryDetail(LoginRequiredMixin, DetailView):
    model = MusicLibrary
    fields = ['name', 'type', 'filepath']


# ------------------------------------------------------------

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
    if request.method == 'GET':
        return render(request, 'tunes/musiclibraryplaylist_form.html', context=context)
    if request.method == 'POST':
        key = request.user.pk
        owner = get_object_or_404(User, pk=key)
        try:
            playlist = Playlist.objects.get(name=thepl.name, owner=owner)
        except Playlist.DoesNotExist:
            playlist = Playlist()
            playlist.name = thepl.name
            playlist.owner = owner
            playlist.save()
        # add all the songs to this playlist.
        for song in song_list:
            savesong(song, owner, playlist)
        thepl.loaded = True
        thepl.save()
        # return render(request, thepl.library.get_absolute_url(), context=context)
        return redirect(thepl.library.get_absolute_url(), context=context)


def savesong(song, o, playlist):
    try:
        t = Tune.objects.get(tune_content=song.location)
    except Tune.DoesNotExist:
        t = Tune()
        t.owner = o
        if song.artist:
            t.artist = song.artist
        t.title = song.name
        if song.album:
            t.album = song.album
        t.tune_content = song.location
        t.save()
    playlist.tunes.add(t)
    playlist.save()


# ------------------------------------------------------------
class FilteredListView(ListView):
    filterset_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class TuneListView(LoginRequiredMixin, FilteredListView):
    model = Tune
    template_name = 'tunes/tune_search.html'
    paginate_by = 25
    filterset_class = TuneFilter

    def get(self, request):
        # dont display query set until a query form is filled in.
        if 'title' not in request.GET:
            filterset = TuneFilter(request.GET)
            return render(request, 'tunes/tune_search.html', {'filterset': filterset})
        else:
            return super().get(request)


# ----------------------------------------------------------------------------------------
@login_required
def create_playlist(request):
    form = TuneSearchForm()
    if request.method == 'GET':
        if 'title' in request.GET:
            form = TuneSearchForm(request.GET)
            if form.is_valid():
                tunes = Tune.objects.all()
                if 'artist' in request.GET:
                    artist_search = form.cleaned_data.get('artist')
                    if artist_search:
                        tunes = tunes.filter(artist__icontains=artist_search)
                if 'title' in request.GET:
                    title_search = form.cleaned_data.get('title')
                    if title_search:
                        tunes = tunes.filter(title__icontains=title_search)
                if 'album' in request.GET:
                    album_search = form.cleaned_data.get('album')
                    if album_search:
                        tunes = tunes.filter(album__icontains=album_search)
                return render(request, 'tunes/playlist_create.html', {'tune_list': tunes, 'form': form})
    if request.method == 'POST':
        name = request.POST['name']
        tune_list = request.POST.getlist('tune')
        u = get_object_or_404(User, pk=request.user.pk)
        try:
            pl = Playlist()
            pl.name = name
            pl.owner = u
            pl.save()
        except IntegrityError:
            # playlist already exists. just add the tunes to the playlist.
            pl = get_object_or_404(Playlist, name=name)
        for t in tune_list:
            onetune = get_object_or_404(Tune, pk=t)
            pl.tunes.add(onetune)
        return redirect(pl.get_absolute_url(), {'form': form})
    return render(request, 'tunes/playlist_create.html', {'form': form})
