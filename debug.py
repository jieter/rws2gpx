#!/usr/bin/env python
import os
import sys
import zipfile

from rws2gpx import areas, convert_file, geojson_polygon


def debug_bounds():
    'Returns a GeoJSON string to inspect the bounds (for example in geojson.io)'
    import json

    features = []
    for name, bounds in areas.items():
        features.append(geojson_polygon([[
            bounds[0][::-1],
            [bounds[1][1], bounds[0][0]],
            bounds[1][::-1],
            [bounds[0][1], bounds[1][0]],
            bounds[0][::-1]
        ]], name=name))

    return json.dumps({
        'type': 'FeatureCollection',
        'features': features
    })


def debug_icons(data):
    with zipfile.ZipFile('UserIcons.zip', 'r') as z:
        z.extractall(os.path.join('debug', 'UserIcons'))

    unique = set()
    for row in data:
        raw = row['raw']
        unique.add((raw['OBJ_VORM'], raw['OBJ_KLEUR'], raw['TT_TOPTEK'], raw['TT_KLEUR']))

    print 'Unieke vorm/kleur/topteken-combinaties: ', len(unique)

if __name__ == '__main__':
    if not os.path.exists('debug'):
        os.mkdir('debug')

    with open(os.path.join('debug', 'bounds.geojson'), 'w') as outfile:
        outfile.write(debug_bounds())

        print('Wrote bounds .geojson to debug/bounds.geojson')


    if len(sys.argv) == 2:
        data = convert_file(sys.argv[1])

        debug_icons(data)
