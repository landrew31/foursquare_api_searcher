import os
import logging
from pprint import pprint


def configure_logger(name):
    log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    log.addHandler(console_handler)
    return log

category_prefix_mapper = {
    '4d4b7104d754a06370d81259': 'arts_entertainment',
    '4d4b7105d754a06374d81259': 'food',
    '4d4b7105d754a06377d81259': 'outdoors',
    '4d4b7105d754a06378d81259': 'shop_service',
    '4d4b7105d754a06379d81259': 'travel_transport',
}

category_subfields = [
    'count',
    'checkins_count',
    'tip_count',
    'users_count',
    'visits_count',
    'likes_count',
    'average_rating',
    'with_rating_count',
]

log = configure_logger(__name__)


def ensure_dir(directory):
    if not os.path.exists(directory):
        log.info('New Directory /{}/ created'.format(directory))
        os.mkdir(directory)


def get_venue_fields():
    return [
        'id',
        'name',
        'formattedAddress',
        'lat',
        'lng',
        'checkinsCount',
        'tipCount',
        'usersCount',
        'visitsCount',
        'likesCount',
        'rating',
        'categories_ids',
        'categories_names',
        'ratingSignals',
    ]


def get_venue_dict(raw_venue):
    v = raw_venue
    loc = v.get('location', {})
    stats = v.get('stats', {})
    return {
        'id': v.get('id'),
        'name': v.get('name'),
        'formattedAddress': loc.get('formattedAddress'),
        'lat': loc.get('lat'),
        'lng': loc.get('lng'),
        'checkinsCount': stats.get('checkinsCount'),
        'tipCount': stats.get('tipCount'),
        'usersCount': stats.get('usersCount'),
        'visitsCount': stats.get('visitsCount'),
        'likesCount': v.get('likes', {}).get('count'),
        'rating': v.get('rating', 0),
        'categories_ids': [cat['id'] for cat in v['categories'] if cat.get('id')],
        'categories_names': [cat['name'] for cat in v['categories'] if cat.get('name')],
        'ratingSignals': v.get('ratingSignals', 0),
    }


def get_category_fields():
    return [
        'id',
        'name',
        'categories',
    ]


def get_category_dict(raw_category):
    return {
        'id': raw_category.get('id'),
        'name': raw_category.get('name'),
        'categories': [cat['id'] for cat in raw_category.get('categories') if cat.get('id')],
    }


def get_category_sub_fields_dict(line, cat_prefix):
    sub_fields = {
        'count' : 1,
        'checkins_count': int(line.get('checkinsCount', 0) or 0),
        'tip_count': int(line.get('tipCount', 0) or 0),
        'users_count': int(line.get('usersCount', 0) or 0),
        'visits_count': int(line.get('visitsCount', 0) or 0),
        'likes_count': int(line.get('likesCount', 0) or 0),
        'average_rating': float(line.get('rating', 0) or 0),
        'with_rating_count': 1 if float(line.get('rating', 0)) else 0,
    }
    return {'{}_{}'.format(cat_prefix, field): val for field, val in sub_fields.items() }


def get_aggregated_venue_fields():
    fields = [
        'region_number',
        'top_latitude',
        'bottom_latitude',
        'top_longitude',
        'bottom_longitude',
        'all_count',
    ]
    for cat in category_prefix_mapper.values():
        fields.extend([
            '{}_{}'.format(cat, sub_field) for sub_field in category_subfields
        ])
    return fields


def add_venue_to_region_dict(region_dict, venue):
    average_key = ''
    rating_counts_key = ''
    for key, value in venue.items():
        if 'average_rating' not in key:
            region_dict[key] += value
        elif value:
            average_key = key
        if 'with_rating_count' in key and value:
            rating_counts_key = key
    # pprint(venue)
    if venue.get(rating_counts_key):
        print(average_key, venue[average_key], venue[rating_counts_key], rating_counts_key)
    if venue.get(rating_counts_key):
        # print(venue[average_key], region_dict[average_key], region_dict[rating_counts_key])
        region_dict[average_key] = venue[average_key]
    return region_dict


def normalize_average(region_dict):
    for key, value in region_dict.items():
        if 'average_rating' in key:
            cat_prefix = key[:len(key)-len('average_rating') - 1]
            if region_dict[key]:
                region_dict[key] = region_dict[key] / region_dict['{}_with_rating_count'.format(
                    cat_prefix,
                )]
    return region_dict


def get_mid_point(loc):
    mid_lat = float(loc['top_latitude']) / 2 + float(loc['bottom_latitude']) / 2
    mid_long = float(loc['top_longitude']) / 2 + float(loc['bottom_longitude']) / 2
    mid_lat = "{0:.6f}".format(mid_lat)
    mid_long = "{0:.6f}".format(mid_long)
    return mid_lat, mid_long


def create_square(top_lat, top_long, bot_lat, bot_long):
    return {
        'top_latitude': top_lat,
        'top_longitude': top_long,
        'bottom_latitude': bot_lat,
        'bottom_longitude': bot_long
    }


def get_four_split_squares(loc):
    mid_lat, mid_long = get_mid_point(loc)
    return [
        create_square(loc['top_latitude'], loc['top_longitude'], mid_lat, mid_long),
        create_square(mid_lat, mid_long, loc['bottom_latitude'], loc['bottom_longitude']),
        create_square(mid_lat, loc['top_longitude'], loc['bottom_latitude'], mid_long),
        create_square(loc['top_latitude'], mid_long, mid_lat, loc['bottom_longitude']),
    ]


def string_repr_into_array(str_array):
    return list(map(lambda x: x[1:-1], str_array[1:-1].split(', ')))