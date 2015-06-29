__author__ = 'brnr'

import logging
import logging.config
import os.path

if os.path.isfile('logging.conf'):
    logging.config.fileConfig('logging.conf')
