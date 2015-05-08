__author__ = 'brnr'

import os
import yaml
import logging
import sys
import json

from dynamite.INIT.DynamiteConfig import *

from dynamite.GENERAL.DynamiteExceptions import IllegalArgumentError
from dynamite.GENERAL.DynamiteExceptions import ServiceFileNotFoundError
from dynamite.GENERAL.DynamiteExceptions import DuplicateServiceFileError

logging.basicConfig(format='%(asctime)s %(message)s')


class DYNAMITE_ENVIRONMENT_STRUCT(object):
    PRODUCTION = "PRODUCTION"
    DEVELOPMENT = "DEVELOPMENT"
    TEST = "TEST"


# # Takes a >> PATH/unit_file_name << as argument
# # Returns a python list-object (which can then be encoded to json)
# def unit2list(unit_file_w_path):
#     logging.info('Starting Converting Fleet-Unit File into Python-List')
#     logging.info('File to be converted:' + unit_file_w_path)
#
#     data = {}
#     data["desiredState"] = "loaded"
#     data["options"] = []
#
#     with open(unit_file_w_path, 'r') as infile:
#         section = ""
#         for line in infile:
#             if line.rstrip() == "[Unit]":
#                 section = "Unit"
#                 logging.info("[Unit]")
#                 continue
#             elif line.rstrip() == "[Service]":
#                 section = "Service"
#                 logging.info("[Service]")
#                 continue
#             elif line.rstrip() == "[X-Fleet]":
#                 section = "X-Fleet"
#                 logging.info("[X-Fleet]")
#                 continue
#             elif line.rstrip() == "":
#                 continue
#             elif line.strip()[0] == "#":
#                 continue
#
#             line = line.rstrip()
#             name,value = line.split("=" , 1)
#             logging.info(name, "=", value)
#
#             option = {}
#             option["section"] = section
#             option["name"] = name
#             option["value"] = value
#
#             data["options"].append(option)
#
#     return data
#
#
# # Takes a >> PATH/unit_file_name << as argument
# # Returns a json-object
# # Uses <<unit2list>> function
# def unit2json(unit_file_w_path):
#     python_object = unit2list(unit_file_w_path)
#     json_object = json.dumps(python_object)
#     return json_object
#
#
# # Takes a DynamiteConfig object which contains the name of the required service files as well as the paths where
# # those service files lie
# # Converts those service-files
# # Returns a dictionary containing json-objects of those service-files
# def service_files_list_2_json_list(dynamite_config):
#
#     # Return Variable: Will contain converted unit-files
#     json_list = []
#
#     if not isinstance(dynamite_config, DynamiteConfig):
#         raise IllegalArgumentError("Expected Instance of DynamiteConfig")
#
#     # Get the name of the service files as defined in the dynamite configuration file
#     # (dynamite_config.Service.<name>.name_of_unit_file
#     name_of_service_files = []
#     for service_attributes in dynamite_config.Service.__dict__.values():
#         name_of_service_files.append(service_attributes.name_of_unit_file)
#
#     # key is name of the file, value is path of the file
#     dict_of_files = {}
#
#     # create a dictionary (files --> path) of the files contained in the folder in dynamite_config.ServiceFiles.PathList
#     for service_file_folder in dynamite_config.ServiceFiles.PathList:
#         list_of_files = os.listdir(service_file_folder)
#
#         for file in list_of_files:
#             abs_path_of_file = os.path.join(service_file_folder, file)
#             if os.path.isfile(abs_path_of_file):
#                 if file in dict_of_files:
#                     raise DuplicateServiceFileError("Error: " + file + " was found 2 times")
#                 else:
#                     dict_of_files[file] = abs_path_of_file
#
#     # Check if one of the folders in Dynamite.PathList contain one of the services specified in Dynamite.Service
#     # If
#     for service in name_of_service_files:
#         if service in dict_of_files:
#             json_object = unit2json(dict_of_files[service])
#             json_list.append(json_object)
#         else:
#             raise ServiceFileNotFoundError(service + " Service-File was not found")
#
#     return json_list


if __name__ == '__main__':

    path_to_config_file = "..\\tests\\TEST_CONFIG_FOLDER\\config.yaml"
    service_folder_list = ['C:\\Users\\brnr\\PycharmProjects\\dynamite\\dynamite\\tests\\TEST_CONFIG_FOLDER\\service-files']

    dynamite_config = DynamiteConfig(path_to_config_file)