from django.urls import path

from tunes import views

urlpatterns = [

    path('', views.index, name='index'),

    path('playlists/', views.PlaylistListView.as_view(),              name='playlists'),
    path('playlist/<int:pk>', views.PlaylistDetail.as_view(),         name='playlist_detail'),

    path('playlist/create/',  views.create_playlist,                  name='playlist_create'),
    path('playlist/<int:pk>/delete/', views.PlaylistDelete.as_view(), name='playlist_delete'),
    path('playlist/<int:pk>/play/', views.PlaylistPlay.as_view(),     name='playlist_play'),

    path('register/', views.register,                                 name='register'),
    path('user/<int:pk>/update/', views.UserUpdate.as_view(),         name='update_user'),
    path('geouser/<int:pk>/update/', views.GeoUserUpdate.as_view(),   name='geouser_update'),
    path('password/', views.change_password,                          name='change_password'),

    path('tune/create/', views.TuneCreate.as_view(),                  name='tune_create'),
    path('tune/<int:pk>/getLyrics/', views.get_lyrics,                name='get_lyrics'),
    path('missing_lyrics/', views.get_missing_lyrics,                  name='missing_lyrics'),
    path('tune/<int:pk>/delete/', views.TuneDelete.as_view(),         name='tune_delete'),
    path('tunes/search/', views.TuneListView.as_view(),               name='tune_search'),
    path('song/<int:pk>', views.song,                                 name='tune_detail'),
    path('tunes/link/', views.LinkCreate.as_view(),                   name='tune_link'),

    path('usertunelocation/<int:pk>/delete/', views.UserTuneLocationDelete.as_view(), name='link_delete'),

    path('locations/search/', views.GeoLocationList.as_view(),        name='location_search'),
    path('mylocations/', views.MyGeoLocationList.as_view(),           name='my_location_list'),
    path('location/<int:pk>/update', views.GeoLocationUpdate.as_view(), name='geolocation_update'),
    path('location/create/', views.GeoLocationCreate.as_view(),       name='geolocation_create'),


    path('libraries/', views.LibraryList.as_view(),                   name='libraries'),
    path('library/create/', views.LibCreate.as_view(),                name='library_create'),
    path('library/<int:pk>', views.LibraryDetail.as_view(),           name='library_detail'),
    path('libplaylist/<int:pk>', views.libplaylistload,               name='load_playlist'),

]
