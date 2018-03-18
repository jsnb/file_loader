import os
import unittest
import argparse

from file_loader.file_handler import FileHandler
from file_loader.logger import logger

from config import SPECS_DIR, DATA_DIR, DATABASE_CONFIG, FAILED_DIR, ARCHIVE_DIR, FIXED_WIDTH


def run_tests(verbosity=2):
    tests = unittest.TestLoader().discover('test/')
    unittest.TextTestRunner(verbosity=verbosity).run(tests)


if __name__ == '__main__':
    commands = ['test', 'load']
    parser = argparse.ArgumentParser()
    parser.add_argument('command', help='action you want to perform',
                        type=str, choices=['test', 'load'])
    parser.add_argument('-f', '--file', action='store', help='use this flag to parse/load a single file')
    parser.add_argument('-a', '--all', action='store_true', help='parse and load all files in the data/ dir')
    parser.add_argument('-w', '--watch', action='store_true', help='constantly watch the data/ dir for incoming files')
    parser.add_argument('-b', '--backend', action='store', choices=DATABASE_CONFIG.keys(), default='sqlite',
                        help='choose a backend from the available backends defined in the config file')

    args = parser.parse_args()

    if args.command == 'test':
        run_tests()
    if args.command == 'load':
        if args.all:
            # only check for files
            files = [f for f in os.listdir(DATA_DIR) if os.path.isfile(os.path.join(DATA_DIR,f))]

        if args.file:
            files = [args.file]

        connection_string = DATABASE_CONFIG.get(args.backend)

        logger.info('sending `%s` files to the file handler', len(files))
        file_handler = FileHandler(
            DATA_DIR, SPECS_DIR, FAILED_DIR, ARCHIVE_DIR, args.backend,
            FIXED_WIDTH, connection_string, files
        )

        file_handler.run()

        if args.watch:
            print('TODO watchdog dir...')
