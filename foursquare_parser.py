import csv
import os

from foursquare import Foursquare

from helpers import (
    configure_logger,
    get_category_dict,
    get_category_fields,
    get_venue_dict,
    get_venue_fields,
    get_four_split_squares,
    ensure_dir,
)


log = configure_logger(__name__)


KYIV_SQUARE = {
    'top_latitude': '50.370877',
    'top_longitude': '30.338019',
    'bottom_latitude': '50.523706',
    'bottom_longitude': '30.680739',
}

SUBSQUARE_SIZE = 0.01
DIRECTORY_PATTERN = 'data_{step}'.format(step=SUBSQUARE_SIZE)
FILE_NAME_PATTERN = '{dir}/foursquare_venues_info_{num}.csv'

SECRETS = [
    {
        'client_id': 'SCCALEKAQBLZ12ZOZ350IRAKINTU44FQFV2M5U4SYKFJQUZE',
        'client_secret': 'K2SLCAL3HQDSCDM21JYTXA5ZGPWJPQXP2FWA4GBX5UOEQKLQ',
    },
    {
        'client_id': 'YG5ZNP20FTHLWWREAEUOXUBSGARUZDPUQ5PB3Q55LEPQTSQ5',
        'client_secret': 'UDZHWREXNOHNGWVBZG2SD1AFLTLNKHOKGEHZLIHZXEKJUHTP',
    },
    {
        'client_id': '1CVW4TUW3TAR2LC3XAOR3UVO4NYPB2AG1TP5BMIEJSRAR1ZT',
        'client_secret': 'CNCXEQV14CVPEMQPJTU2ZVDITXGQPKBT0M00KQ3IDRPCHQ3J',
    },
]


client = Foursquare(
    client_id=SECRETS[1].get('client_id'),
    client_secret=SECRETS[1].get('client_secret'),
    version='20170514',
)


def process_raw_category(raw, sub_cats_list):
    for sub_raw in raw['categories']:
        sub_cats_list = list(
            set(sub_cats_list) & set(process_raw_category(sub_raw, sub_cats_list))
        )
        sub_cats_list.extend(sub_cats_list)
    return sub_cats_list


def parse_categories():
    with open('foursquare_categories_info_v2.csv', mode='w') as f:
        fieldnames = get_category_fields()
        writer = csv.DictWriter(f, fieldnames)
        writer.writeheader()
        cats = client.venues.categories().get('categories')
        for cat in cats:
            d = get_category_dict(cat)
            d['categories'] = process_raw_category(cat, d['categories'])
            log.info('Going to write category: {}'.format(d))
            writer.writerow(d)


def process_venues(ids, writer):
    venue_info = [
        get_venue_dict(
            client.venues(venue_id).get('venue')
        ) for venue_id in ids
    ]
    log.debug('Going to write {num} venues'.format(num=len(venue_info)))
    for info in venue_info:
        writer.writerow(info)


def process_square(location, writer):
    venues_req = client.venues.search(params={
        'sw': '{},{}'.format(
            location.get('top_latitude'),
            location.get('top_longitude'),
        ),
        'ne': '{},{}'.format(
            location.get('bottom_latitude'),
            location.get('bottom_longitude'),
        ),
        'intent': 'browse',
        'limit': 50,
    })
    venues = venues_req.get('venues')

    log.info('Got {num} venues.'.format(num=len(venues)))

    if len(venues) == 50:
        splitted_locations = get_four_split_squares(location)
        for loc in splitted_locations:
            process_square(loc, writer)
    else:
        foursquare_ids = [v['id'] for v in venues]
        log.info('Going to write {num} venues: {ids}'.format(
            num=len(foursquare_ids),
            ids=foursquare_ids,
        ))
        process_venues(foursquare_ids, writer)


def parse_venues(location, number):
    ensure_dir(DIRECTORY_PATTERN)
    file_name = FILE_NAME_PATTERN.format(
        dir=DIRECTORY_PATTERN,
        num=number,
    )
    with open(file_name, mode='w') as f:
        fieldnames = get_venue_fields()
        writer = csv.DictWriter(f, fieldnames)
        writer.writeheader()
        log.info('Gonna start processing venues!')
        process_square(location, writer)


def get_max_col_size():
    top_longitude = float(KYIV_SQUARE['top_longitude'])
    bottom_longitude = float(KYIV_SQUARE['bottom_longitude'])
    return int((bottom_longitude - top_longitude) / SUBSQUARE_SIZE) + 1


def get_max_row_size():
    top_latitude = float(KYIV_SQUARE['top_latitude'])
    bottom_latitude = float(KYIV_SQUARE['bottom_latitude'])
    return int((bottom_latitude - top_latitude) / SUBSQUARE_SIZE) + 1


def get_max_number():
    return get_max_col_size() * get_max_row_size()


def get_kyiv_square_by_number(number):
    top_latitude = float(KYIV_SQUARE['top_latitude'])
    top_longitude = float(KYIV_SQUARE['top_longitude'])
    bottom_latitude = float(KYIV_SQUARE['bottom_latitude'])
    bottom_longitude = float(KYIV_SQUARE['bottom_longitude'])
    max_col_size = int((bottom_longitude - top_longitude) / SUBSQUARE_SIZE) + 1
    max_row_size = int((bottom_latitude - top_latitude) / SUBSQUARE_SIZE) + 1
    max_square_number = max_row_size * max_col_size
    log.info('Max square number for Kyiv: {}={}x{}'.format(
        max_square_number, max_row_size, max_col_size
    ))
    if number > max_square_number or number < 1:
        raise ValueError('Wrong square number. Select value from 1 to {}'.format(max_square_number))
    number -= 1
    row_num = int(number / max_col_size)
    col_num = number - row_num * max_col_size
    base_hor = top_longitude + SUBSQUARE_SIZE * col_num
    base_ver = top_latitude + SUBSQUARE_SIZE * row_num
    return {
        'top_latitude': base_ver,
        'top_longitude': base_hor,
        'bottom_latitude': (
            base_ver + SUBSQUARE_SIZE
            if base_ver + SUBSQUARE_SIZE < bottom_latitude
            else bottom_latitude
        ),
        'bottom_longitude': (
            base_hor + SUBSQUARE_SIZE
            if base_hor + SUBSQUARE_SIZE < bottom_longitude
            else bottom_longitude
        ),
    }


def parse_map(start_parse_number=1):
    ensure_dir(DIRECTORY_PATTERN)
    for i in range(start_parse_number, get_max_number() + 1):
        if not os.path.exists(FILE_NAME_PATTERN.format(
            dir=DIRECTORY_PATTERN,
            num=i,
        )):
            log.info('Going to parse venues for square: {}'.format(i))
            parse_venues(get_kyiv_square_by_number(i), i)
        else:
            log.info('Venues for square: {} already exists!'.format(i))
