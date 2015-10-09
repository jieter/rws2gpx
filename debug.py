#!/usr/bin/env python
import os
import sys
import zipfile

from rws2gpx import areas, convert_file, geojson_polygon, shapes, topmarks


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


html_format = '''
<html>
<head>
    <title>User icon debug page</title>
    <style>
    i {
        border: 1px solid #aaa;
        position: relative;
        display: block;
        width: 100px;
        height: 96px;
        padding: 0;
        margin-left: 4px;
        margin-bottom: 4px;
        float: left;
    }
    i * {
        position: absolute;
    }
    i img {
        top: 0;
        left: 14px;
    }
    i span {
        left: 0;
        width: 100px;
        text-align: center;
        bottom: 0;
        font-size: 10px;
    }
    </style>
</head>
<body>
<h2>UserIcons debug page</h2>
%s
</body>
</html>
'''

icon_format = '''<i>
    <img src="UserIcons/{shape}.png" />
    <img src="UserIcons/{topmark}.png" />
    <span>{topmark}<br />{shape}</span>
</i>'''

colors = [
    'Green',
    'Red',
    'Yellow',
]

def debug_icons():
    with zipfile.ZipFile('UserIcons.zip', 'r') as z:
        z.extractall(os.path.join('debug', 'UserIcons'))

    icons = []
    for s in shapes.values():
        for i, t in enumerate(topmarks.values()):
            if 'TODO' in t:
                continue

            icons.append(icon_format.format(**{
                'shape': '%s_%s' % (s, colors[i % len(colors)]),
                'topmark': 'Top_' + t
            }))

    with open(os.path.join('debug', 'index.html'), 'w') as h:
        h.write(html_format % '\n'.join(icons))

def unique_icons(data):
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

    debug_icons()

    if len(sys.argv) == 2:
        data = convert_file(sys.argv[1])

        unique_icons(data)
