import sys
from foursquare_parser import (
    parse_venues,
    parse_map,
    parse_categories,
)
from aggregator import (
    regionalize_files,
    aggregate_info,
)
from spatial_module import (
    make_weights,
    calculate_gamma_index,
    calculate_join_count_statistics,
    calculate_moran_i,
    calculate_geary_c,
    calculate_local_moran,
    calculate_local_getis_and_ord,
    calculate_ols,
)
from command_executor import CommandExecutor


command_mapper = {
    'run_from_number': CommandExecutor(parse_map, (int,)),
    'get_categories': CommandExecutor(parse_categories),
    'parse_square': CommandExecutor(parse_venues, (int,)),
    'regionalize': CommandExecutor(regionalize_files, (int, int)),
    'aggregate': CommandExecutor(aggregate_info),
    'make_weights': CommandExecutor(make_weights),
    'gamma_index': CommandExecutor(calculate_gamma_index),
    'join_count_statistic': CommandExecutor(calculate_join_count_statistics),
    'moran_one': CommandExecutor(calculate_moran_i),
    'geary_c': CommandExecutor(calculate_geary_c),
    'local_moran': CommandExecutor(calculate_local_moran),
    'local_getis_ord': CommandExecutor(calculate_local_getis_and_ord),
    'ols': CommandExecutor(calculate_ols),
}


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception('Use some of commands!')

    command = command_mapper.get(sys.argv[1])

    if not command:
        raise Exception('Unknown command!')

    arguments = sys.argv[2:]
    command.validate(arguments)
    command()
