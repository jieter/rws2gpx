# GeoJSON export functions
def feature(feature_type, coordinates, properties=None, **kwargs):
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


def polygon(coords, properties=None, **kwargs):
    return feature('Polygon', coords, properties, **kwargs)


def point(coord, properties=None, **kwargs):
    return feature('Point', coord, properties, **kwargs)
