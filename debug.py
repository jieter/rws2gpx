#!/usr/bin/env python

# Some methods to debug/test aspects of converting Rijkswaterstaat's CSV file
# to GPX format
from __future__ import print_function

import os
import sys
import zipfile

import geojson
from rws2gpx import areas, convert_file, shape, topmark, light


def debug_bounds():
    'Returns a GeoJSON string to check the bounds (for example in geojson.io)'
    import json

    features = []
    for name, bounds in areas.items():
        features.append(geojson.polygon([[
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


html_header = '''<html>
<head>
    <title>User icon debug page</title>
    <link rel="stylesheet" type="text/css" href="style.css">
</head>
<body>
'''
html_footer = '</body></html>'

icon_fmt = '<img src="UserIcons/{}.png" />'
buoy_fmt = '''<i>
{icons}
<table>
    <tr><td></td><th>RWS CSV</th><th>User icon</th></tr>
    <tr><td>Shape:</td><td>{OBJ_VORM}, {OBJ_KLEUR}</td><td>{shape}</td></tr>
    <tr><td>Topmark:</td><td>{TT_TOPTEK}, {TT_KLEUR}</td><td>{topmark}</td></tr>
    <tr><td>Light:</td><td>{LICHT_KLR}</td><td>{light}</td></tr>
</table>
</i>'''

def render_buoy(shape, topmark=None, light=None, **kwargs):
    icons = icon_fmt.format(shape)
    if topmark:
        icons += icon_fmt.format(topmark)
    if light:
        icons += icon_fmt.format(light)

    return buoy_fmt.format(icons=icons, shape=shape, topmark=topmark, light=light, **kwargs)

def extract_icons(output_path):
    icons_path = os.path.join(output_path, 'UserIcons')
    if os.path.exists(icons_path):
        return

    with zipfile.ZipFile('UserIcons.zip', 'r') as z:
        z.extractall(icons_path)

    print('Extracted UserIcons to %s' % icons_path)


def unique_icons(data):
    unique = set()
    # these are the keys we're interested in to map to user icons
    keys = ['OBJ_VORM', 'OBJ_KLEUR', 'TT_TOPTEK', 'TT_KLEUR', 'LICHT_KLR']

    for row in data:
        raw = row['raw']

        unique.add(tuple(raw[key] for key in keys))

    print('Unieke vorm/kleur/topteken-combinaties: {}'.format(len(unique)))

    # for i in unique:
    #     print(i)
    # transform to a list of dicts again for easy parsing
    return ({key: item[i] for i, key in enumerate(keys)} for item in unique)


if __name__ == '__main__':
    DEBUG_PATH = 'debug'
    if not os.path.exists(DEBUG_PATH):
        os.mkdir(DEBUG_PATH)
    extract_icons(DEBUG_PATH)

    with open(os.path.join(DEBUG_PATH, 'bounds.geojson'), 'w') as outfile:
        outfile.write(debug_bounds())

        print('Wrote bounds .geojson to debug/bounds.geojson')

    if len(sys.argv) == 2:
        unique_buoys = unique_icons(convert_file(sys.argv[1]))

        buoys = []
        for buoy in unique_buoys:
            buoy['shape'] = shape(buoy)
            if buoy['TT_TOPTEK'] != 'Niet toegewezen':
                buoy.update(topmark=topmark(buoy))
            if buoy['LICHT_KLR'] != 'Niet toegewezen':
                buoy.update(light=light(buoy))
            buoys.append(render_buoy(**buoy))


        with open(os.path.join(DEBUG_PATH, 'index.html'), 'w') as h:
            h.write(html_header)
            h.write('<h2>Icon combinations</h2>')
            h.write('\n'.join(buoys))
            h.write(html_footer)
