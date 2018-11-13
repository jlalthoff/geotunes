from django.urls import path
from tunes import views

urlpatterns = [

    path('', views.index, name='index'),

    path('playlists/', views.PlaylistListView.as_view(),              name='playlists'),
    path('playlist/<int:pk>', views.PlaylistDetail.as_view(),         name='playlist_detail'),
    path('playlist/create/', views.PlaylistCreate.as_view(),          name='playlist_create'),
    path('playlist/<int:pk>/update/', views.PlaylistUpdate.as_view(), name='playlist_update'),
    path('playlist/<int:pk>/delete/', views.PlaylistDelete.as_view(), name='playlist_delete'),
    path('playlist/<int:pk>/play/',  views.PlaylistPlay.as_view(),    name='playlist_play'),

    path('register/', views.register,                               name='register'),
    path('user/<int:pk>/update/',   views.UserUpdate.as_view(),     name='update_user'),
    path('password/', views.change_password,                        name='change_password'),

    path('tune/create/', views.TuneCreate.as_view(),                name='tune_create'),
    path('tune/<int:pk>/delete/', views.TuneDelete.as_view(),       name='tune_delete'),
    path('tunes/', views.TuneListView.as_view(),                    name='tunes'),
    path('song/<int:pk>', views.song,                               name='tune_detail'),
    path('tunes/link/', views.LinkCreate.as_view(),                 name='tune_link'),
    path('usertunelocation/<int:pk>/delete/', views.UserTuneLocationDelete.as_view(), name='link_delete'),

    path('locations/', views.GeoLocationList.as_view(),             name='location_list'),
    path('mylocations/', views.MyGeoLocationList.as_view(),         name='my_location_list'),
    path('locations/search/', views.GeoLocationList.as_view(),      name='location_search'),
    path('location/<int:pk>', views.GeoLocationDetail.as_view(),    name='geolocation_detail'),
    path('location/<int:pk>/update', views.GeoLocationUpdate.as_view(), name='geolocation_update'),
    path('location/create/', views.GeoLocationCreate.as_view(),     name='geolocation_create'),

    path('geouser/<int:pk>/update/', views.GeoUserUpdate.as_view(),  name='geouser_update'),



]

