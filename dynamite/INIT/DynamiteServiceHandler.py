__author__ = 'brnr'

import json
import os
import logging

from dynamite.GENERAL.DynamiteExceptions import IllegalArgumentError
from dynamite.GENERAL.DynamiteExceptions import ServiceFileNotFoundError
from dynamite.GENERAL.DynamiteExceptions import DuplicateServiceFileError

from dynamite.INIT.DynamiteConfig import DynamiteConfig

# DynamiteServiceHandler    - converts service-files (fleet) to json objects
#                           - shows information about the services it handles
#                           - talks to fleet (opens connection, publishes to fleet, add, removes services from fleet
class DynamiteServiceHandler(object):
    # Instance Variables
    DynamiteConfig = None
    ServiceJSONObjectDict = {}          # service-file-name --> json-object #### change to service-file-name --> FleetService object
    # FleetServiceDict = {}

    # Takes a >> PATH/unit_file_name << as argument
    # Returns a python list-object (which can then be encoded to json)
    def unit2list(self, unit_file_w_path):
        logging.info('Starting Converting Fleet-Unit File into Python-List')
        logging.info('File to be converted:' + unit_file_w_path)

        data = {}
        data["desiredState"] = "inactive"
        data["options"] = []

        with open(unit_file_w_path, 'r') as infile:
            section = ""
            for line in infile:
                if line.rstrip() == "[Unit]":
                    section = "Unit"
                    logging.info("[Unit]")
                    continue
                elif line.rstrip() == "[Service]":
                    section = "Service"
                    logging.info("[Service]")
                    continue
                elif line.rstrip() == "[X-Fleet]":
                    section = "X-Fleet"
                    logging.info("[X-Fleet]")
                    continue
                elif line.rstrip() == "":
                    continue
                elif line.strip()[0] == "#":
                    continue

                line = line.rstrip()
                name,value = line.split("=" , 1)
                logging.info(name, "=", value)

                option = {}
                option["section"] = section
                option["name"] = name
                option["value"] = value

                data["options"].append(option)

        return data


    # Takes a >> PATH/unit_file_name << as argument
    # Returns a json-object
    # Uses <<unit2list>> function
    def unit2json(self, unit_file_w_path):
        python_object = self.unit2list(unit_file_w_path)
        json_object = json.dumps(python_object)
        return json_object


    # Takes a DynamiteConfig object which contains the name of the required service files as well as the paths where
    # those service files lie
    # Converts those service-files
    # Returns a dictionary containing json-objects of those service-files --> service-name --> json-object
    def dynamite_config_2_json_dict(self, dynamite_config):

        json_dict = {}

        if not isinstance(dynamite_config, DynamiteConfig):
            raise IllegalArgumentError("Error: Argument not instance of type 'DynamiteConfig'")

        # Get the name of the service files as defined in the dynamite configuration file
        # (dynamite_config.Service.<name>.name_of_unit_file
        name_of_service_files = []
        for service_attributes in dynamite_config.Service.__dict__.values():
            name_of_service_files.append(service_attributes.name_of_unit_file)

        # key is name of the file, value is path of the file
        dict_of_files = {}

        # create a dictionary (files --> path) of the files contained in the folder in dynamite_config.ServiceFiles.PathList
        for service_file_folder in dynamite_config.ServiceFiles.PathList:
            list_of_files = os.listdir(service_file_folder)

            for file in list_of_files:
                abs_path_of_file = os.path.join(service_file_folder, file)
                if os.path.isfile(abs_path_of_file):
                    if file in dict_of_files:
                        raise DuplicateServiceFileError("Error: " + file + " was found 2 times")
                    else:
                        dict_of_files[file] = abs_path_of_file

        # Check if one of the folders in Dynamite.PathList contains one of the services specified in Dynamite.Service
        # If fleet unit-file is found, it is converted to a json object
        for service in name_of_service_files:
            if service in dict_of_files:
                json_object = self.unit2json(dict_of_files[service])
                json_dict[service] = json_object
            else:
                raise ServiceFileNotFoundError(service + " Service-File was not found")

        return json_dict

    def __init__(self, dynamite_config):
        if not isinstance(dynamite_config, DynamiteConfig):
            raise IllegalArgumentError("Error: Argument not instance of type 'DynamiteConfig'")

        self.ServiceJSONObjectDict = self.dynamite_config_2_json_dict(dynamite_config)

    def __str__(self):
        pass


if __name__ == '__main__':

    path_to_config_file = "..\\tests\\TEST_CONFIG_FOLDER\\config.yaml"
    service_folder_list = ['C:\\Users\\brnr\\PycharmProjects\\dynamite\\dynamite\\tests\\TEST_CONFIG_FOLDER\\service-files']

    dynamite_config = DynamiteConfig(path_to_config_file, service_folder_list)

    service_handler = DynamiteServiceHandler(dynamite_config)

    # for key, value in service_handler.ServiceJSONObjectDict.items():
    #     print(key)
    #     print(value)

    #print(service_handler.ServiceJSONObjectDict)

    example_service_json = service_handler.ServiceJSONObjectDict['example.service']

    # cwd = os.path.abspath(os.path.dirname(__file__))
    # print(cwd)

    # print(example_service_json)
    # print(type(example_service_json))

    with open('..\\tests\\TEST_CONFIG_FOLDER\\json-files\\example.service.json', 'w') as outfile:
        outfile.write(example_service_json)