# -*- coding: utf-8 -*-

import sys
from datetime import datetime

import ijson


def create_feature(obj):
    return {
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [
                obj['longitudeE7'] / 10000000.0,
                obj['latitudeE7'] / 10000000.0
            ]
        },
        'properties': {
            'accuracy': obj.get('accuracy', None),
            'timestamp': datetime.fromtimestamp(int(obj['timestampMs']) / 1000.0).isoformat()
        }
    }


def parse_location(stream):
    parser = ijson.parse(stream)
    reading = False
    obj = {}
    key = None
    value = None
    for prefix, event, value in parser:
        if prefix == 'locations' and event == 'start_array':
            reading = True
        elif prefix == 'locations' and event == 'end_array':
            reading = False
        elif reading:
            if event == 'start_map' and prefix == 'locations.item':
                obj = {}
            elif event == 'end_map' and prefix == 'locations.item':
                yield create_feature(obj)
            elif event == 'map_key':
                key = value
            elif prefix == 'locations.item.%s' % key and value is not None:
                obj[key] = value


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print 'Specify filname'
        exit(0)

    filename = sys.argv[1]
    with open(filename, 'r') as file:
        for feature in parse_location(file):
            print feature
