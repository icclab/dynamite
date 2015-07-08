__author__ = 'brnr'

import logging
import logging.config
import os
import os.path

log_config_path = os.environ.get("DYNAMITE_LOG_CONFIG_PATH", "logging.conf")
if os.path.isfile(log_config_path):
    logging.config.fileConfig(log_config_path)
