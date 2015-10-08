#!/usr/bin/env python


# dirived from
# https://github.com/nohal/OpenCPNScripts/blob/master/rws_buoys2gpx-osmicons.sh

import csv
import os
import sys

areas = {
    'IJsselmeerS': [[52.2, 4.55], [52.9, 6.1]],
    'IJselmeerN_WaddenzeeW': [[52.9, 4.55], [53.5, 5.75]],
    'WaddenzeeE': [[53.1, 5.2], [53.6, 7.2]],
    'Zeeland': [[51.2, 3.15], [52.14, 4.9]],
    'alles': [[50, 1.5], [55, 9]]
}

def debug_bounds():
    import json

    features = []
    for name, bounds in areas.items():
        features.append({
            'type': 'Feature',
            'properties': {'name': name},
            'geometry': {
                'type': 'Polygon',
                'coordinates': [[
                    bounds[0][::-1],
                    [bounds[1][1], bounds[0][0]],
                    bounds[1][::-1],
                    [bounds[0][1], bounds[1][0]],
                    bounds[0][::-1]
                ]]
            }
        })

    return json.dumps({
        'type': 'FeatureCollection',
        'features': features
    })



gpx_format = '''<?xml version="1.0"?>
<gpx version="1.0" creator="rws2gpx.py">
{}
</gpx>'''

gpx_waypoint_format = '''<wpt lat="{lat}" lon="{lon}">
    <type>WPT</type>
    <name>{name}</name>
    <sym>{symbol}</sym>
</wpt>'''

shapes = {
    'stomp': 'Can',
    'spits': 'Cone',
    'spar': 'Beacon',
    'bol': 'Sphere',
    'pilaar': 'Pillar',
    # er zijn nu (2015-10-08) twee objecten met OBJ_VORM 'ton'
    'ton': 'Beacon',
    'vast': 'Tower'
}
colors = {
    'rood': 'Red',
    'rood/groen': 'Sphere_Red_Green_Red',
    'rood/groen repeterend': 'Red_Green_Red_Green',
    'rood/wit': 'Sphere_Red_White',
    'rood/wit repeterend': 'Red_White_Red_White',
    'rood/groen/rood': 'Red_Green_Red',

    'geel': 'Yellow',
    'geel/zwart': 'Yellow_Black',
    'geel/zwart/geel': 'Yellow_Black_Yellow',
    'geel/zwart/geel': 'Beacon_Yellow_Black_Yellow',

    'zwart/geel': 'Black_Yellow',
    'zwart/geel/zwart': 'Black_Yellow_Black',
    'zwart/rood/zwart': 'Beacon_Black_Red_Black',

    'groen': 'Green',
    'groen/wit repeterend': 'Green_White_Green_White',
    'groen/rood': 'Green_Red',
    'groen/rood/groen': 'Green_Red_Green'
}
lights = {
    'wit': 'Light_White_120',
    'groen': 'Light_Green_120',
    'Rood': 'Light_Red_120',
    'Geel': 'Light_White_120',
}
# topmarks = {
#     'liggend_kruis':
# }

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
    return 'Top_{}_{}'.format(1, 2)

def convert_row(row):
    return {
        'lon': coord(row['X_WGS84']),
        'lat': coord(row['Y_WGS84']),
        'vaarwater': row['VAARWATER'],
        'symbol': symbol(row),
        'name': row['BENAMING'],
        # 'topmark': symbol(row, keys=('TT_TOPTEK', 'TT_KLEUR')),
        # ''

        # 'raw': row
    }

def convert_file(filename):
    data = []
    with open(filename) as csvfile:
        for row in csv.DictReader(csvfile, delimiter=';'):
            try:
                data.append(convert_row(row))
            except NoCoordsException:
                print('Geen coordinaten: %s' % row['BENAMING'])
            except Exception as e:
                print('Failed parsing: %s' % str(e))
                for item in row.items():
                    print('%20s: %s' % item)
    return data

def gpx_waypoint(x):
    return gpx_waypoint_format.format(**x)

def bounds_contain(bounds):
    def contains(data):
        return (
            bounds[0][1] < data['lon'] < bounds[1][1] and
            bounds[0][0] < data['lat'] < bounds[1][0]
        )
    return contains

def gpx(data):
    waypoints = map(gpx_waypoint, data)
    return gpx_format.format('\n'.join(waypoints))


if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == 'bounds':
            print(debug_bounds())
            sys.exit()

        data = convert_file(sys.argv[1])

        if not os.path.exists('output'):
            os.mkdir('output')
        print('Write ')
        print('%6s | %10s' % ('aantal', 'bestandsnaam'))
        for filename, bounds in areas.items():
            filtered_data = filter(bounds_contain(bounds), data)
            with open(os.path.join('output', filename + '.gpx'), 'w') as outfile:
                outfile.write(gpx(filtered_data))
            print('%6d | %s.gpx' % (len(filtered_data), filename))


    else:
        print('''Usage:
rws2gpx.py <filename>''')
