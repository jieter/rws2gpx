#!/usr/bin/env python


# dirived from
# https://github.com/nohal/OpenCPNScripts/blob/master/rws_buoys2gpx-osmicons.sh

import csv
import sys

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

def gpx(rows):
    waypoints = map(gpx_waypoint, rows)
    return gpx_format.format('\n'.join(waypoints))

if __name__ == '__main__':
    if len(sys.argv) == 2:
        data = convert_file(sys.argv[1])

        with open('output.gpx', 'w') as outfile:
            outfile.write(gpx(data))

    else:
        print('''Usage:
rws2gpx.py <filename>''')
