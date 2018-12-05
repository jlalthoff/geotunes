from GEO import settings

from tunes.Library import Library
from tunes.models import Tune
from django.contrib.auth.models import User

import django
django.setup()
settings.configure()

l = Library("/Users/jerryalthoff/Music/iTunes/iTunes Music Library.xml")

print (settings.INSTALLED_APPS)

o = User.objects.get(username='jerryalthoff')

def run(playlist_name):
    for song in l.getPlaylist(playlist_name).tracks:
        print(song.location_escaped, '======', song.name, ' BY ', song.artist)
        t = Tune()
        try:
            t.owner = o
            t.artist = song.artist
            t.title = song.name
            t.tune_url = song.location_escaped
            t.save()
            print('Saved')
        except:
            print(song.name,' NOT SAVED')

run('All Time Top Ten')
