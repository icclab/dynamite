__author__ = 'brnr'

import logging

from dynamite.INIT.DynamiteConfig import *

logging.basicConfig(format='%(asctime)s %(message)s')


class DYNAMITE_ENVIRONMENT_STRUCT(object):
    PRODUCTION = "PRODUCTION"
    DEVELOPMENT = "DEVELOPMENT"
    TEST = "TEST"


class DYNAMITE_APPLICATION_STATUS(object):
    NONE = None                         # Before applicaton starts for the first time
    INITIALIZING = "Initializing"       # Before application is running for the first time
    RUNNING = "Running"                 # Status after 'Initializing' or after 'Recovering'
    RECOVERING = "Recovering"           # After application came back up and
    DEAD = "Dead"                       # After being in status 'Recovering' for too long
    ALLOWED_VALUES = [None, "Initializing", "Running", "Recovering", "Dead"]


if __name__ == '__main__':

    path_to_config_file = "..\\tests\\TEST_CONFIG_FOLDER\\config.yaml"
    service_folder_list = ['C:\\Users\\brnr\\PycharmProjects\\dynamite\\dynamite\\tests\\TEST_CONFIG_FOLDER\\service-files']

    dynamite_config = DynamiteConfig(path_to_config_file)