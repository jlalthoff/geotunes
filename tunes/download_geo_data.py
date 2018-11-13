import os

"""
download the cartographic boundary files for each state from 
the us census website
unzip the file
then load it into a postgres temp table
and insert it into the master geolocations table
"""


def run():
    nn = 56
    state = format(nn, '02d')
    xxx = '/Users/jerryalthoff/OSGEO\ Share/cb_2017_' + state + '_place_500k.zip'
    os.system('unzip ' + xxx + ' -d /tmp/geodata/' + state)
    print('OK>' + xxx)
    return 'Good'


def run2():
    # for n in range(1, 60):
    #     if n not in (3, 7, 8, 14, 18, 21, 26, 39, 54, 57, 58, 59):
    n=45
    cmda = 'shp2pgsql -d -s 4269:4326 /tmp/geodata/'
    cmdb = '/cb_2017_'
    cmdc = '_place_500k.shp public.temp_locations  |psql -d tunes -U django'

    cmd2 = 'psql -d tunes -U django -f /tmp/geodata/load_locations.sql'
    cmd1 = cmda + format(n, '02d') + cmdb + format(n, '02d') + cmdc
    os.system(cmd1)
    os.system(cmd2)


run2()

"""
shp2pgsql -d -s 4269:4326 /tmp/geodata/08/cb_2017_08_place_500k.shp public.temp_locations  |psql -d tunes -U django

psql -d tunes -U django -f /tmp/geodata/load_locations.sql


load_locations.sql File contains: 

select count(*) from tunes_geolocation;

insert into tunes_geolocation(name, type, state, area, geom) 
select b.name, 'PLACE', a.stusps, b.aland, b.geom 
from temp_locations b, states a where a.statefp = b.statefp;

select count(*) from tunes_geolocation;

\q


"""
