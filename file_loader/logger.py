import logging
from logging.handlers import RotatingFileHandler

# create logger
logger = logging.getLogger('Parser App')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
#handler = logging.StreamHandler()

LOG_FILENAME = 'logs/file_load.log'

handler = RotatingFileHandler(LOG_FILENAME, maxBytes=200000, backupCount=5)

handler.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
handler.setFormatter(formatter)

# add ch to logger
logger.addHandler(handler)

# 'application' code
logger.info('log initialized %s' % __name__)
