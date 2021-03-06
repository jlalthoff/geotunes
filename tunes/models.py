from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.urls import reverse  # Used to generate URLs by reversing the URL patterns


# --------------------------------------------------------------------------------

class GeoUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    default_center_point = models.PointField(blank=True, default=Point(-88, 42))

    def __str__(self):
        return self.user.get_username()

    def get_absolute_url(self):
        """Returns the url to access a particular instance of the model."""
        return reverse('geouser-detail-view', args=[str(self.id)])

    @receiver(post_save, sender=User)
    def create_geouser(sender, instance, created, **kwargs):
        if created:
            GeoUser.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_geouser(sender, instance, **kwargs):
        instance.geouser.save()

    class Meta:
        ordering = ['user']


# --------------------------------------------------------------------------------

LIBRARY_TYPES = (
    ('iTunes', 'Apple Itunes Music Library'),
    ('other', 'To Be Determined'),
)


class MusicLibrary(models.Model):
#TODO add UI to delete MusicLibray
    name = models.CharField(max_length=30, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=12, choices=LIBRARY_TYPES, default='iTunes')
    filepath = models.FileField(max_length=1000, upload_to='Users/jerryalthoff/uploads/%Y/%m/%d', unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a particular instance of the model."""
        return reverse('library_detail', args=[str(self.id)])

    class Meta:
        ordering = ['name']

@receiver(pre_delete, sender=MusicLibrary)
def musiclibrary_delete(sender, instance, **kwargs):
    # Pass false so FileField does not save the model
    #only delete if the tune_content in not the empty string (not null column)
    if instance.filepath:
        instance.filepath.delete(False)

# --------------------------------------------------------------------------------
class MusicLibraryPlaylist(models.Model):
    name = models.CharField(max_length=100)
    library = models.ForeignKey(MusicLibrary, on_delete=models.CASCADE)
    loaded = models.BooleanField(default=True)

    def __str__(self):
        return 'name' + ' IN ' + self.library.name

    class Meta:
        ordering = ['name']


# --------------------------------------------------------------------------------
class Playlist(models.Model):
    name = models.CharField(max_length=100)
    date_created = models.DateTimeField('date created', auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    tunes = models.ManyToManyField('Tune')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a particular instance of the model."""
        #  return reverse('playlist_detail', args=[str(self.id)])
        return reverse('playlist_detail', kwargs={'pk': self.pk})

    class Meta:
        unique_together = ('owner', 'name')
        ordering = ['name']


# --------------------------------------------------------------------------------

class Tune(models.Model):
    LYRICS_STATUS = (
        ('FOUND', 'Lyrics Found'),
        ('NOT FOUND', 'Lyrics Not Found'),
        ('TO SEARCH', 'No search performed')
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    artist = models.CharField(max_length=100, default='unknown')
    title = models.CharField(max_length=200)
    album = models.CharField(max_length=200, default='None')
    lyrics = models.TextField()
    lyrics_status = models.CharField(max_length=12, choices=LYRICS_STATUS, default='TO SEARCH')
    tune_content = models.FileField(max_length=1000, upload_to='Users/jerryalthoff/uploads/%Y/%m/%d', unique=True)

    def __str__(self):
        return self.title + ' By ' + self.artist

    def get_absolute_url(self):
        """Returns the url to access a particular instance of the model."""
        return reverse('tune_detail', args=[str(self.id)])

    class Meta:
        unique_together = ('artist', 'title', 'album')
        ordering = ['artist', 'title']

@receiver(pre_delete, sender=Tune)
def tune_delete(sender, instance, **kwargs):
    # Pass false so FileField does not save the model
    # only delete those that were uploaded into media (under Users) directory
    #only delete if the tune_content in not the empty string (not null column)
    if instance.tune_content and str(instance.tune_content).startswith('Users'):
        instance.tune_content.delete(False)
# --------------------------------------------------------------------------------


class State(models.Model):
    state = models.CharField(max_length=12)
    code = models.CharField(max_length=2, default='00')
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.state + ':' + self.name + '-' + self.code

    class Meta:
        ordering = ['name']


# --------------------------------------------------------------------------------
class GeoLocation(models.Model):
    LOCATION_TYPES = (
        ('COUNTY', 'Counties of the United States'),
        ('PLACE', 'Place or populated area'),
        ('STATE', 'State of the United States'),
        ('PARK', 'US National Park'),
        ('USER', 'User defined area')
    )
    owner = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    type = models.CharField(max_length=12, choices=LOCATION_TYPES, default='USER')
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    area = models.BigIntegerField(default=0)

    geom = models.MultiPolygonField(srid=4326)

    def __str__(self):
        return self.type + ':' + self.name + '(' + self.state + ')'

    def get_absolute_url(self):
        """Returns the url to access a particular instance of the model."""
        return reverse('geolocation_detail', args=[str(self.id)])

    class Meta:
        ordering = ['type', 'name', 'state']


# --------------------------------------------------------------------------------

class UserTuneLocation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tune = models.ForeignKey(Tune, on_delete=models.CASCADE)
    location = models.ForeignKey(GeoLocation, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.__str__() + ': ' + \
               self.tune.__str__() + ' at ' + \
               self.location.__str__()

    def get_absolute_url(self):
        """Returns the url to access a particular instance of the model."""
        return reverse('tune_detail', args=[str(self.tune.id)])
