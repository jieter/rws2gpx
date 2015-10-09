#!/usr/bin/env python
import glob
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


html_header = '''
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
        display: block;
        bottom: 0;
        font-size: 10px;
    }
    h2 {
        clear: both;
    }
    </style>
</head>
<body>
'''

buoy_fmt = '''<i>
    <img src="UserIcons/{shape}.png" />
    <img src="UserIcons/{topmark}.png" />
    <span>{topmark}<br />{shape}</span>
</i>'''
icon_fmt = '<i><img src="UserIcons/{}" /><span>{}</span></i>'

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

            icons.append(buoy_fmt.format(**{
                'shape': '%s_%s' % (s, colors[i % len(colors)]),
                'topmark': 'Top_' + t
            }))
    all_icons = []
    for i in glob.glob('debug/UserIcons/*.png'):
        if 'Notice' in i:
            continue
        i = i.split('/')[-1]
        all_icons.append(icon_fmt.format(i, i))

    with open(os.path.join('debug', 'index.html'), 'w') as h:
        h.write(html_header)
        h.write('<h2>Combined icons</h2>')
        h.write('\n'.join(icons))
        h.write('<h2>All icons:</h2>')
        h.write('\n'.join(all_icons))
        h.write('</body></html>')


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
