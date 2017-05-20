import csv
import os
import sys
from helpers import (
    get_category_fields,
    get_venue_fields,
    get_aggregated_venue_fields,
    configure_logger,
    ensure_dir,
    category_prefix_mapper,
    get_category_sub_fields_dict,
    add_venue_to_region_dict,
    string_repr_into_array,
    normalize_average,
    sum_general,
)
from foursquare_parser import (
    get_max_col_size,
    get_max_row_size,
    DIRECTORY_PATTERN,
    FILE_NAME_PATTERN,
    get_kyiv_square_by_number,
)

CATEGORIES_FILTERED_FILE_NAME = 'foursquare_categories_info_filtered.csv'
REGIONALIZED_DIRECTORY = 'regionalized'
REGIONALIZED_FILE_PATTERN = 'regionalized/venues_info_{num}.csv'
AGGREGATED_FILE_NAME = 'aggregated_info.csv'


log = configure_logger(__name__)


def regionalize_files(lat_part, long_part):
    rows = get_max_row_size()
    cols = get_max_col_size()
    start_rows_in_one = int(rows / lat_part)
    start_cols_in_one = int(cols / long_part)
    cells = {}
    for i in range(lat_part):
        for j in range(1, long_part + 1):
            sub_cells = []
            for a in range(start_rows_in_one):
                for b in range(1, start_cols_in_one + 1):
                    sub_cells.append((i * start_rows_in_one + a) * cols + (j - 1) * start_cols_in_one + b)
            cells[i * long_part + j] = sub_cells

    ensure_dir(REGIONALIZED_DIRECTORY)
    for number, sub_cells in cells.items():
        file_name = REGIONALIZED_FILE_PATTERN.format(num=number)
        log.info('Is going to write file {}'.format(file_name))
        with open(file_name, 'w') as f:
            fieldnames = get_venue_fields()
            writer = csv.DictWriter(f, fieldnames)
            writer.writeheader()
            for sub_cell in sub_cells:
                source_file_name = FILE_NAME_PATTERN.format(
                    dir=DIRECTORY_PATTERN,
                    num=sub_cell,
                )
                source_file = open(source_file_name, 'r')
                reader = csv.DictReader(source_file, fieldnames)
                log.debug('Opened file: {}'.format(source_file_name))
                for index, line in enumerate(reader):
                    if index != 0:
                        writer.writerow(line)
                log.debug('Processed file: {}'.format(source_file_name))
        log.info('File wrote: {}'.format(file_name))


def aggregate_info():
    num_files = len([
        f for f in os.listdir(REGIONALIZED_DIRECTORY)
        if os.path.isfile(os.path.join(REGIONALIZED_DIRECTORY, f)) and f.endswith('.csv')
    ])
    cats_dict = {}
    with open(CATEGORIES_FILTERED_FILE_NAME, 'r') as cats_file:
        cats_reader = csv.DictReader(cats_file, get_category_fields())
        for index, line in enumerate(cats_reader):
            if index:
                cats_dict[line['id']] = set(string_repr_into_array(line['categories']))
                cats_dict[line['id']].add(line['id'])

    with open(AGGREGATED_FILE_NAME, 'w') as aggregate_file:
        writer = csv.DictWriter(aggregate_file, get_aggregated_venue_fields())
        writer.writeheader()
        for num in range(1, num_files + 1):
            region_dict = {field: 0 for field in get_aggregated_venue_fields()}
            region_dict['region_number'] = num
            file_name = REGIONALIZED_FILE_PATTERN.format(num=num)
            log.info('Is going to aggregate file: {}'.format(file_name))
            with open(file_name, 'r') as f:
                reader = csv.DictReader(f, get_venue_fields())
                for index, line in enumerate(reader):
                    if index:
                        venue = {field: 0 for field in get_aggregated_venue_fields()[5:]}
                        ids = set(string_repr_into_array(line['categories_ids']))
                        good_cat = False
                        for key, val in cats_dict.items():
                            if val & ids:
                                good_cat = True
                                sub_fields_dict = get_category_sub_fields_dict(line, category_prefix_mapper.get(key))
                                venue.update(sub_fields_dict)

                        if good_cat:
                            venue['all_count'] += 1
                            region_dict = add_venue_to_region_dict(region_dict, venue)

            kyiv_sub_square = get_kyiv_square_by_number(num, 0.02, 0.05)
            region_dict.update(kyiv_sub_square)

            log.info('Is going to write {} aggregated venues for region #{}'.format(
                region_dict['all_count'], num
            ))
            region_dict = sum_general(region_dict)
            region_dict = normalize_average(region_dict)
            writer.writerow(region_dict)
