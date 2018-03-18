# default the sqlite db to the current directory
import os

cwd = os.getcwd()
DB_FILE = 'clover.db'
SQLITE_URL = os.path.join(cwd,DB_FILE)

DATABASE_CONFIG = {
    'sqlite': 'sqlite:////%s' % SQLITE_URL
}

SPECS_DIR = './specs'
DATA_DIR = './data'
ARCHIVE_DIR = './data/loaded'
FAILED_DIR = './data/failed'

FIXED_WIDTH = 'fixed_width'

LOG_FILENAME = 'logs/file_load.log'
