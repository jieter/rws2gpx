#!/usr/bin/env python

# This code is derived from/inspired by:
# https://github.com/nohal/OpenCPNScripts/blob/master/rws_buoys2gpx-osmicons.sh

from __future__ import division, print_function

import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime
from shutil import copyfile


def error(*args, **kwargs):
    'Print to stderr'
    print(file=sys.stderr, *args, **kwargs)


# a file in geojson format is expected with polygons having a 'name' property
# which is used to name the output files.
BOUNDS_PATH = 'bounds.geojson'


def point_in_poly(x, y, poly):
    # function from http://geospatialpython.com/2011/01/point-in-polygon.html
    n = len(poly)
    inside = False

    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


def areas():
    '''
    yield (name, test)-tuples for the area's. The test function expects a
    dict-like object with keys 'lat' and 'lon' to test if the object falls
    within the polygon.
    '''
    with open(BOUNDS_PATH) as gj:
        bounds = json.load(gj)

    for feature in bounds['features']:
        if feature['geometry']['type'] != 'Polygon':
            # skip non-polygon geometries
            continue

        def test(data):
            '''
            Test whether the point represented by data is within the current polygon
            '''
            return point_in_poly(
                data['lon'],
                data['lat'],
                feature['geometry']['coordinates'][0]
            )
        yield (feature['properties']['name'], test)


gpx_format = '''<?xml version="1.0"?>
<gpx version="1.0" creator="rws2gpx.py">
<metadata>{metadata}</metadata>
{waypoints}
</gpx>'''

gpx_metadata_fmt = '''
<desc>Created from Rijkswaterstaat data from http://www.vaarweginformatie.nl/fdd/main/infra/downloads,
source filename: {csv_file}</desc>
<time>{created}</time>'
'''

NOT_ASSIGNED = 'Niet toegewezen'

shapes = {
    'bol': 'Sphere',
    'pilaar': 'Pillar',
    'spar': 'Beacon',
    'spits': 'Cone',
    'stomp': 'Can',
    # er zijn nu (2015-10-08) twee objecten met OBJ_VORM 'ton'
    'ton': 'Can',
    'vast': 'Tower'
}

# map dutch color combinations to a color from the UserIcons
colors = {
    'rood': 'Red',
    'rood/groen': 'Sphere_Red_Green_Red',
    'rood/groen repeterend': 'Red_Green_Red_Green',
    'rood/groen/rood': 'Red_Green_Red',
    'rood/wit': 'Sphere_Red_White',
    'rood/wit repeterend': 'Red_White_Red_White',
    'rood/wit/rood': 'Red_White_Red',

    'geel': 'Yellow',
    'geel/zwart': 'Yellow_Black',
    'geel/zwart/geel': 'Yellow_Black_Yellow',

    'zwart': 'Black',
    'zwart/geel': 'Black_Yellow',
    'zwart/geel/zwart': 'Black_Yellow_Black',
    'zwart/rood/zwart': 'Black_Red_Black',

    'groen': 'Green',
    'groen/wit repeterend': 'Green_White_Green_White',
    'groen/rood': 'Green_Red',
    'groen/rood/groen': 'Green_Red_Green'
}

# map dutch light colors to User icons
light_colors = {
    'geel': 'White',
    'groen': 'Green',
    'rood': 'Red',
    'wit': 'White'
}

# map dutch top mark names to User icons
topmarks = {
    'bol': 'Sphere',
    'cilinder': 'Can',
    'cilinder boven bol': 'TODO',
    'kruis': 'Cross_Yellow',
    'liggend kruis': 'Cross_Yellow',
    'staand kruis': 'Cross_Yellow',
    'kegel, punt naar boven': 'Cone',
    'kegel boven bol': 'TODO',

    '2 bollen': 'Isol',
    '2 kegels, punten naar beneden': 'South',
    '2 kegels punten van elkaar af': 'East',
    '2 kegels, punten naar elkaar': 'West',
    '2 kegels, punten naar boven': 'North'
}


class NoCoordsException(Exception):
    pass


def coord(x):
    if x == '#WAARDE!':
        raise NoCoordsException
    return float(x.replace(',', '.'))


def shape(x):
    return '{}_{}'.format(
        shapes[x['OBJ_VORM'].lower()],
        colors[x['OBJ_KLEUR'].lower()]
    )


def topmark(x):
    top = x['TT_TOPTEK'].lower()
    shape = x['OBJ_VORM'].lower()

    ext = ''
    if top in ('cilinder', 'bol') or top.startswith('kegel'):
        ext += '_' + colors[x['TT_KLEUR'].lower()]

    if 'kruis' in top:
        ext += '_Beacon'
    elif shape in ('spits', 'stomp', 'bol'):
        ext += '_Buoy_Small'
    elif shape == 'pilaar':
        ext += '_Buoy'
    else:
        ext += '_Beacon'

    return 'Top_{}{}'.format(
        topmarks[top],
        ext
    )


def light(x):
    return 'Light_{}_120'.format(light_colors[x['LICHT_KLR'].lower()])


def convert_row(row):
    ret = {
        'lon': coord(row['X_WGS84']),
        'lat': coord(row['Y_WGS84']),
        'vaarwater': row['VAARWATER'],
        'symbol': shape(row),
        'name': row['BENAMING'],
        'raw': row
    }

    if row['TT_TOPTEK'] != NOT_ASSIGNED:
        ret.update(topmark=topmark(row))
    if row['LICHT_KLR'] != NOT_ASSIGNED:
        ret.update(light=light(row))

    return ret


def convert_file(filename, verbose=False):
    data = []
    errors = defaultdict(list)

    with open(filename) as csvfile:
        for row in csv.DictReader(csvfile, delimiter=';'):
            if len(row['OBJ_VORM']) == 0 or row['OBJ_VORM'] == NOT_ASSIGNED:
                errors['failed'].append(row['BENAMING'])
                continue
            try:
                data.append(convert_row(row))
            except NoCoordsException:
                errors['coords'].append(row['BENAMING'])
            except Exception as e:
                errors['failed'].append(row['BENAMING'])
                if verbose:
                    error('Failed parsing: %s' % str(e))
                    for item in row.items():
                        error('%20s: %s' % item)

    if len(errors['coords']) > 0:
        error('Geen coordinaten voor: {}'.format(', '.join(errors['coords'])))
    if len(errors['failed']) > 0:
        error('Niet kunnen parsen: {}'.format(', '.join(errors['failed'])))
    return data


# GPX export functions
def gpx_waypoint(data=None, type='WPT', **kwargs):
    data = data.copy() or {}
    data.update(kwargs)
    body = []
    if type is not None:
        body.append('\t<type>{}</type>'.format(type))
        body.append('\t<name>{}</name>'.format(data['name']))

    description = []
    raw = data['raw']
    description.append('Vaarwater: %s' % raw['VAARWATER'])
    description.append('Kleur: %s' % raw['OBJ_KLEUR'])
    if raw['SIGN_KAR'] != NOT_ASSIGNED:
        description.append('Lichtkarakter: %s' % raw['SIGN_KAR'])
        description.append('Lichtkleur: %s' % raw['LICHT_KLR'])

    body.append('\t<desc>{}</desc>'.format('\n'.join(description)))
    body.append('\t<sym>{}</sym>'.format(data['symbol']))

    return '<wpt lat="{lat}" lon="{lon}">\n{body}\n</wpt>'.format(
        body='\n'.join(body),
        **data
    )


def gpx_topmark_waypoint(data):
    if 'topmark' not in data:
        return None

    return gpx_waypoint(data, type=None, symbol=data['topmark'])


def gpx_light_waypoint(data):
    if 'light' not in data:
        return None

    return gpx_waypoint(data, type=None, symbol=data['light'])


def gpx(data, metadata=''):
    waypoints = map(gpx_waypoint, data)
    # waypoints.extend(map(gpx_topmark_waypoint, data))
    # waypoints.extend(map(gpx_light_waypoint, data))

    waypoints = filter(lambda x: x is not None, waypoints)
    return gpx_format.format(metadata=metadata, waypoints='\n'.join(waypoints))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage:\nrws2gpx.py <filename>')
        sys.exit()

    csv_file = sys.argv[1]
    if not os.path.isfile(csv_file):
        error('Input file %s does not exist' % csv_file)
        sys.exit(1)

    if not os.path.exists('output'):
        os.mkdir('output')

    metadata = gpx_metadata_fmt.format(
        csv_file=csv_file,
        created='{}Z'.format(datetime.utcnow().replace(microsecond=0).isoformat())
    )

    data = convert_file(csv_file)

    out_path = os.path.join('output', os.path.basename(csv_file).split('.')[0])
    if not os.path.exists(out_path):
        os.mkdir(out_path)

    print('\nWriting output to GPX files:')
    print('%7s | %s' % ('# buoys', 'filename'))

    for bounds_name, bounds_test in areas():
        filtered_data = list(filter(bounds_test, data))
        out_filename = os.path.join(out_path, bounds_name + '.gpx')

        with open(out_filename, 'w') as outfile:
            outfile.write(gpx(filtered_data, metadata=metadata))
        print('%7d | %s.gpx' % (len(filtered_data), bounds_name))

    copyfile(BOUNDS_PATH, os.path.join(out_path, 'bounds.geojson'))
