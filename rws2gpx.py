#!/usr/bin/env python

# This code is derived from/inspired by:
# https://github.com/nohal/OpenCPNScripts/blob/master/rws_buoys2gpx-osmicons.sh

from __future__ import print_function

import csv
import os
import sys
from datetime import datetime
from collections import defaultdict


def error(*args, **kwargs):
    'Print to stderr'
    print(file=sys.stderr, *args, **kwargs)

# geo bounds for different output files
areas = {
    'alles': [[50, 1.5], [55, 9]],

    'Lauwersmeer': [[53.33, 6.054], [53.5, 6.26]],
    'IJsselmeerS': [[52.2, 4.55], [52.9, 6.1]],
    'IJselmeerN_WaddenzeeW': [[52.9, 4.55], [53.5, 5.75]],
    'WaddenzeeE': [[53.1, 5.2], [53.6, 7.2]],
    'Zeeland': [[51.2, 3.15], [52.14, 4.9]],
}

gpx_format = '''<?xml version="1.0"?>
<gpx version="1.0" creator="rws2gpx.py">
<metadata>{metadata}</metadata>
{waypoints}
<gpx>'''

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
    return 'Light_{}_120'.format(
        light_colors[x['LICHT_KLR'].lower()]
    )


def convert_row(row):
    ret = {
        'lon': coord(row['X_WGS84']),
        'lat': coord(row['Y_WGS84']),
        'vaarwater': row['VAARWATER'],
        'symbol': shape(row),
        'name': row['BENAMING'],
        'raw': row
    }

    if row['TT_TOPTEK'] != 'Niet toegewezen':
        ret.update(topmark=topmark(row))
    if row['LICHT_KLR'] != 'Niet toegewezen':
        ret.update(light=light(row))

    return ret


def convert_file(filename):
    data = []
    errors = defaultdict(list)

    with open(filename) as csvfile:
        for row in csv.DictReader(csvfile, delimiter=';'):
            if len(row['OBJ_VORM']) == 0:
                continue
            try:
                data.append(convert_row(row))
            except NoCoordsException:
                errors['coords'].append(row['BENAMING'])
            except Exception as e:
                errors['failed'].append(row['BENAMING'])
                error('Failed parsing: %s' % str(e))
                for item in row.items():
                    error('%20s: %s' % item)

    error('Geen coordinaten voor: {}'.format(', '.join(errors['coords'])))
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
    if raw['SIGN_KAR'] != 'Niet toegewezen':
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


def gpx(data, metadata=''):
    waypoints = map(gpx_waypoint, data)
    # topmarks = map(gpx_topmark_waypoint, data)
    # waypoints.extend(filter(lambda x: x is not None, topmarks))
    return gpx_format.format(metadata=metadata, waypoints='\n'.join(waypoints))


def bounds_contain(bounds):
    def contains(data):
        return (
            bounds[0][1] < data['lon'] < bounds[1][1] and
            bounds[0][0] < data['lat'] < bounds[1][0]
        )
    return contains


if __name__ == '__main__':
    if len(sys.argv) == 2:
        csv_file = sys.argv[1]
        data = convert_file(csv_file)

        if not os.path.exists('output'):
            os.mkdir('output')

        created = datetime.now().replace(microsecond=0).isoformat()
        metadata = 'Created from filename: {} on {}'.format(csv_file, created)

        print('\nWrite output to GPX files:')
        print('%7s | %s' % ('#marks', 'filename'))
        for filename, bounds in areas.items():
            filtered_data = list(filter(bounds_contain(bounds), data))
            out_filename = os.path.join('output', filename + '.gpx')
            with open(out_filename, 'w') as outfile:
                outfile.write(gpx(filtered_data, metadata=metadata))
            print('%7d | %s.gpx' % (len(filtered_data), filename))

    else:
        print('''Usage:
rws2gpx.py <filename>''')
