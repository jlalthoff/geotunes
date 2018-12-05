# Generated by Django 2.1.3 on 2018-12-05 15:53

from django.conf import settings
import django.contrib.gis.db.models.fields
import django.contrib.gis.geos.point
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GeoLocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('COUNTY', 'Counties of the United States'), ('PLACE', 'Place or populated area'), ('STATE', 'State of the United States'), ('PARK', 'US National Park'), ('USER', 'User defined area')], default='USER', max_length=12)),
                ('name', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=2)),
                ('area', models.BigIntegerField(default=0)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['type', 'name', 'state'],
            },
        ),
        migrations.CreateModel(
            name='GeoUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('default_center_point', django.contrib.gis.db.models.fields.PointField(blank=True, default=django.contrib.gis.geos.point.Point(-88, 42), srid=4326)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['user'],
            },
        ),
        migrations.CreateModel(
            name='MusicLibrary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
                ('type', models.CharField(choices=[('iTunes', 'Apple Itunes Music Library'), ('other', 'To Be Determined')], default='iTunes', max_length=12)),
                ('filepath', models.FileField(max_length=1000, unique=True, upload_to='Users/jerryalthoff/uploads/%Y/%m/%d')),
            ],
        ),
        migrations.CreateModel(
            name='MusicLibraryPlaylist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('loaded', models.BooleanField(default=True)),
                ('library', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tunes.MusicLibrary')),
            ],
        ),
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['date_created', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Tune',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('artist', models.CharField(default='unknown', max_length=100)),
                ('title', models.CharField(max_length=200)),
                ('album', models.CharField(default='None', max_length=200)),
                ('tune_content', models.FileField(max_length=1000, upload_to='uploads/%Y/%m/%d')),
                ('tune_url', models.URLField(max_length=1000, unique=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['artist', 'title'],
            },
        ),
        migrations.CreateModel(
            name='UserTuneLocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tunes.GeoLocation')),
                ('tune', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tunes.Tune')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tunes.GeoUser')),
            ],
        ),
        migrations.AddField(
            model_name='playlist',
            name='tunes',
            field=models.ManyToManyField(to='tunes.Tune'),
        ),
        migrations.AlterUniqueTogether(
            name='playlist',
            unique_together={('owner', 'name')},
        ),
    ]
