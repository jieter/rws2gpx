#!/usr/bin/env python

# Some methods to debug/test aspects of converting Rijkswaterstaat's CSV file
# to GPX format
from __future__ import print_function

import os
import sys
import zipfile

from rws2gpx import areas, convert_file, geojson_polygon


def debug_bounds():
    'Returns a GeoJSON string to check the bounds (for example in geojson.io)'
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


html_header = '''
<html>
<head>
    <title>User icon debug page</title>
    <link rel="stylesheet" type="text/css" href="style.css">
</head>
<body>
'''

buoy_fmt = '''<i>
    <img src="UserIcons/{shape}.png" />
    <img src="UserIcons/{topmark}.png" />
    <span>{topmark}<br />{shape}</span>
</i>'''

icon_fmt = '<i><img src="UserIcons/{}" /><span>{}</span></i>'


def extract_icons(output_path):
    with zipfile.ZipFile('UserIcons.zip', 'r') as z:
        z.extractall(os.path.join(output_path, 'UserIcons'))


def unique_icons(data):
    unique = set()
    # these are the keys we're interested in to map to user icons
    keys = ['OBJ_VORM', 'OBJ_KLEUR', 'TT_TOPTEK', 'TT_KLEUR', 'LICHT_KLR']

    for row in data:
        raw = row['raw']

        item = tuple(raw[key] for key in keys)
        unique.add(item)

    print('Unieke vorm/kleur/topteken-combinaties: {}'.format(len(unique)))

    # transform to a list of dicts again for easy parsing
    return ({key: item[key] for key in keys} for item in unique)


if __name__ == '__main__':
    if not os.path.exists('debug'):
        os.mkdir('debug')

    with open(os.path.join('debug', 'bounds.geojson'), 'w') as outfile:
        outfile.write(debug_bounds())

        print('Wrote bounds .geojson to debug/bounds.geojson')

    if len(sys.argv) == 2:
        extract_icons()

        unique = unique_icons(convert_file(sys.argv[1]))

        buoys = []

        with open(os.path.join('debug', 'index.html'), 'w') as h:
            h.write(html_header)
            h.write('<h2>Icon combinations</h2>')
            h.write('\n'.join(buoys))
            h.write('</body></html>')
