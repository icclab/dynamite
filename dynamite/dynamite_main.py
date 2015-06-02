__author__ = 'brnr'

import sys
import argparse
import os
import platform
import json

# The following is only for usage of this application from the command-line
# And only during development
# The application should later be installed via setup.py
if 'C:\\Users\\brnr\\PycharmProjects\\dynamite\\dynamite' not in sys.path:
    sys.path.append('C:\\Users\\brnr\\PycharmProjects\\dynamite\\dynamite')

if 'C:\\Users\\brnr\\PycharmProjects\\dynamite' not in sys.path:
    sys.path.append('C:\\Users\\brnr\\PycharmProjects\\dynamite')

from dynamite.GENERAL.DynamiteHelper import DYNAMITE_ENVIRONMENT_STRUCT
from dynamite.GENERAL.DynamiteHelper import DYNAMITE_APPLICATION_STATUS
from dynamite.INIT.DynamiteINIT import DynamiteINIT

DYNAMITE_ENVIRONMENT = os.getenv('DYNAMITE_ENVIRONMENT', DYNAMITE_ENVIRONMENT_STRUCT.DEVELOPMENT)

DEFAULT_CONFIG_PATH=None
DEFAULT_SERVICE_FOLDER=None
DEFAULT_ETCD_ENDPOINT="127.0.0.1:4001"

ARG_CONFIG_PATH=None
ARG_SERVICE_FOLDER=None
ARG_ETCD_ENDPOINT=None

def init_env():
    global DEFAULT_CONFIG_PATH
    global DEFAULT_SERVICE_FOLDER

    if platform.system() == 'Windows':
        if DYNAMITE_ENVIRONMENT == DYNAMITE_ENVIRONMENT_STRUCT.PRODUCTION:
            DEFAULT_CONFIG_PATH = 'C:\\Program Files\\Dynamite\\config.yaml'
            DEFAULT_SERVICE_FOLDER = 'C:\\Program Files\\Dynamite\\Service-Files'
        elif DYNAMITE_ENVIRONMENT == DYNAMITE_ENVIRONMENT_STRUCT.DEVELOPMENT:
            DEFAULT_CONFIG_PATH = 'tests\\TEST_CONFIG_FOLDER\\config.yaml'
            DEFAULT_SERVICE_FOLDER = 'tests\\TEST_CONFIG_FOLDER\\service-files'
    elif platform.system()() == 'Linux':
        DEFAULT_CONFIG_PATH = '/etc/dynamite/config.yaml'
        DEFAULT_SERVICE_FOLDER = '/etc/dynamite/service-files'


def init_arguments():
    global ARG_CONFIG_PATH
    global ARG_SERVICE_FOLDER
    global ARG_ETCD_ENDPOINT

    parser = argparse.ArgumentParser()

    parser.add_argument("--config_file", "-c",
                        help="Define Config-File to be used. Default: " + DEFAULT_CONFIG_PATH,
                        nargs='?',
                        default=DEFAULT_CONFIG_PATH)

    parser.add_argument("--service_folder", "-s",
                        help="Define Folder(s) in which dynamite searches for service-files (fleet). Default: " + DEFAULT_SERVICE_FOLDER + ". Can be provided multiple times",
                        nargs='?',
                        action='append')

    parser.add_argument("--etcd_endpoint", "-e",
                        help="Define ETCD Endpoint [IP]:[PORT]. Default: " + DEFAULT_ETCD_ENDPOINT,
                        nargs='?',
                        default=DEFAULT_ETCD_ENDPOINT)

    args = parser.parse_args()

    ARG_ETCD_ENDPOINT = args.etcd_endpoint

    ARG_CONFIG_PATH = args.config_file

    # Test if Config-File exists. If not, terminate application
    if not os.path.exists(ARG_CONFIG_PATH):
        raise FileNotFoundError("--config-file: " + ARG_CONFIG_PATH + " --> File at given config-path does not exist")

    ARG_SERVICE_FOLDER_TMP = args.service_folder if args.service_folder != None else [DEFAULT_SERVICE_FOLDER]

    ARG_SERVICE_FOLDER = []

    # First test if Service-Folder(s) exist. If not, terminate application
    # If folder(s) exist save the absolute path
    for service_file_folder in ARG_SERVICE_FOLDER_TMP:
        if not os.path.isdir(service_file_folder):
            raise NotADirectoryError("--service-folder: " + service_file_folder + " --> Is not a directory")
        if os.path.isabs(service_file_folder):
            ARG_SERVICE_FOLDER.append(service_file_folder)
        else:
            ARG_SERVICE_FOLDER.append(os.path.abspath(service_file_folder))


if __name__ == '__main__':
    init_env()
    init_arguments()

    dynamite_init = DynamiteINIT(ARG_CONFIG_PATH, ARG_SERVICE_FOLDER, ARG_ETCD_ENDPOINT)

    # input("wait. click to add 'a' service")

    for i in range(4):
        dynamite_init.dynamite_service_handler.add_new_fleet_service_instance("a")

    # input("wait. click to remove 'a' service")

    # for i in range(4):
    #     dynamite_init.dynamite_service_handler.remove_fleet_service_instance("a")

    # print("hal")
    # input("wait. click to end")
