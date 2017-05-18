import csv
import os
import sys
from helpers import (
    get_venue_fields,
    configure_logger,
    ensure_dir,
)
from foursquare_parser import (
    get_max_col_size,
    get_max_row_size,
    parse_venues,
    parse_map,
    parse_categories,
    DIRECTORY_PATTERN,
    FILE_NAME_PATTERN,
)


REGIONALIZED_DIRECTORY = 'regionalized'
REGIONALIZED_FILE_PATTERN = 'regionalized/venues_info_{num}.csv'


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
