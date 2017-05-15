
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
