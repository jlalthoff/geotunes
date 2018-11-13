# Generated by Django 2.1.1 on 2018-10-27 14:57

import django.contrib.gis.db.models.fields
import django.contrib.gis.geos.point
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tunes', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='geolocation',
            options={'ordering': ['type', 'name', 'state']},
        ),
        migrations.AlterModelOptions(
            name='geouser',
            options={'ordering': ['user']},
        ),
        migrations.AlterModelOptions(
            name='playlist',
            options={'ordering': ['date_created', 'name']},
        ),
        migrations.AlterModelOptions(
            name='tune',
            options={'ordering': ['author', 'title']},
        ),
        migrations.AlterField(
            model_name='geolocation',
            name='type',
            field=models.CharField(choices=[('PLACE', 'Place or populated area'), ('STATE', 'State of the United States'), ('PARK', 'US National Park'), ('USER', 'User defined area')], default='USER', max_length=12),
        ),
        migrations.AlterField(
            model_name='geouser',
            name='default_center_point',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, default=django.contrib.gis.geos.point.Point(-88, 42), srid=4326),
        ),
    ]