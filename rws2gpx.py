#!/usr/bin/env python


# dirived from
# https://github.com/nohal/OpenCPNScripts/blob/master/rws_buoys2gpx-osmicons.sh

import csv
import os
import sys
from collections import defaultdict

areas = {
    'Lauwersmeer': [[53.33, 6.054], [53.5, 6.26]],
    'IJsselmeerS': [[52.2, 4.55], [52.9, 6.1]],
    'IJselmeerN_WaddenzeeW': [[52.9, 4.55], [53.5, 5.75]],
    'WaddenzeeE': [[53.1, 5.2], [53.6, 7.2]],
    'Zeeland': [[51.2, 3.15], [52.14, 4.9]],
    'alles': [[50, 1.5], [55, 9]],
}

gpx_format = '''<?xml version="1.0"?>
<gpx version="1.0" creator="rws2gpx.py">
{}
</gpx>'''


shapes = {
    'bol': 'Sphere',
    'pilaar': 'Pillar',
    'spar': 'Beacon',
    'spits': 'Cone',
    'stomp': 'Can',
    # er zijn nu (2015-10-08) twee objecten met OBJ_VORM 'ton'
    'ton': 'Beacon',
    'vast': 'Tower'
}
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
    'geel/zwart/geel': 'Beacon_Yellow_Black_Yellow',

    'zwart': 'Black',
    'zwart/geel': 'Black_Yellow',
    'zwart/geel/zwart': 'Black_Yellow_Black',
    'zwart/rood/zwart': 'Beacon_Black_Red_Black',

    'groen': 'Green',
    'groen/wit repeterend': 'Green_White_Green_White',
    'groen/rood': 'Green_Red',
    'groen/rood/groen': 'Green_Red_Green'
}

light_colors = {
    'geel': 'White',
    'groen': 'Green',
    'rood': 'Red',
    'wit': 'White'
}

topmarks = {
    'bol': 'Sphere',
    'cilinder': 'Can_Beacon',
    'cilinder boven bol': 'TODO',
    'kruis': 'Cross_Yellow_Beacon',
    'liggend kruis': 'Cross_Beacon',
    'staand kruis': 'Cross_Beacon',
    'kegel, punt naar boven': 'Cone_Beacon',
    'kegel boven bol': 'TODO',

    '2 bollen': 'Isol',
    '2 kegels, punten naar beneden': 'South_Beacon',
    '2 kegels punten van elkaar af': 'East_Beacon',
    '2 kegels, punten naar elkaar': 'West_Beacon',
    '2 kegels, punten naar boven': 'North_Beacon'
}


class NoCoordsException(Exception):
    pass


def coord(x):
    if x == '#WAARDE!':
        raise NoCoordsException
    return float(x.replace(',', '.'))


def symbol(x):
    return '{}_{}'.format(
        shapes[x['OBJ_VORM'].lower()],
        colors[x['OBJ_KLEUR'].lower()]
    )


def topmark(x):
    # TODO: insert topmark size here.

    ext = ''
    if x['TT_TOPTEK'] == 'Cilinder':
        ext = '_' + colors[x['TT_KLEUR'].lower()]

    return 'Top_{}{}'.format(
        topmarks[x['TT_TOPTEK'].lower()],
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
        'symbol': symbol(row),
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
                print('Failed parsing: %s' % str(e))
                for item in row.items():
                    print('%20s: %s' % item)

    print('Geen coordinaten voor: {}'.format(', '.join(errors['coords'])))
    print('Niet kunnen parsen: {}'.format(', '.join(errors['failed'])))
    return data


# GPX export functions
def gpx_waypoint(data=None, type='WPT', **kwargs):
    data = data.copy() or {}
    data.update(kwargs)
    body = []
    if type is not None:
        body.append('\t<type>{}</type>'.format(type))
        body.append('\t<name>{}</name>'.format(data['name']))

    body.append('\t<sym>{}</sym>'.format(data['symbol']))

    return '<wpt lat="{lat}" lon="{lon}">\n{body}\n</wpt>'.format(
        body='\n'.join(body),
        **data
    )

def gpx_topmark_waypoint(data):
    if 'topmark' in data:
        return gpx_waypoint(data, type=None, symbol=data['topmark'])
    else:
        return None

def gpx(data):
    waypoints = map(gpx_waypoint, data)
    topmarks = map(gpx_topmark_waypoint, data)

#    waypoints.extend(filter(lambda x: x is not None, topmarks))
    return gpx_format.format('\n'.join(waypoints))


# GeoJSON export functions
def geojson_feature(feature_type, coordinates, properties=None, **kwargs):
    properties = properties or {}
    properties.update(kwargs)
    return {
        'type': 'Feature',
        'properties': properties,
        'geometry': {
            'type': feature_type,
            'coordinates': coordinates
        }
    }


def geojson_polygon(coords, properties=None, **kwargs):
    return geojson_feature('Polygon', coords, properties, **kwargs)


def geojson_point(coord, properties=None, **kwargs):
    return geojson_feature('Point', coord, properties, **kwargs)


def bounds_contain(bounds):
    def contains(data):
        return (
            bounds[0][1] < data['lon'] < bounds[1][1] and
            bounds[0][0] < data['lat'] < bounds[1][0]
        )
    return contains


if __name__ == '__main__':
    if len(sys.argv) == 2:
        data = convert_file(sys.argv[1])

        if not os.path.exists('output'):
            os.mkdir('output')

        print('\nWrite output to GPX files:')
        print('%7s | %s' % ('#marks', 'filename'))
        for filename, bounds in areas.items():
            filtered_data = list(filter(bounds_contain(bounds), data))
            with open(os.path.join('output', filename + '.gpx'), 'w') as outfile:
                outfile.write(gpx(filtered_data))
            print('%7d | %s.gpx' % (len(filtered_data), filename))

    else:
        print('''Usage:
rws2gpx.py <filename>''')
