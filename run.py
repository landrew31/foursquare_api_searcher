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
from command_executor import CommandExecutor


command_mapper = {
    'run_from_number': CommandExecutor(parse_map, (int,)),
    'get_categories': CommandExecutor(parse_categories),
    'parse_square': CommandExecutor(parse_venues, (int,)),
    'regionalize': CommandExecutor(regionalize_files, (int, int)),
    'aggregate': CommandExecutor(aggregate_info),
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
