__author__ = 'brnr'

import json
import os
import logging

from dynamite.GENERAL.DynamiteExceptions import IllegalArgumentError
from dynamite.GENERAL.DynamiteExceptions import ServiceFileNotFoundError
from dynamite.GENERAL.DynamiteExceptions import DuplicateServiceFileError
from dynamite.GENERAL.FleetServiceHandler import FleetServiceHandler
from dynamite.GENERAL.FleetService import FleetService

from dynamite.INIT.DynamiteConfig import DynamiteConfig

# DynamiteServiceHandler    - converts service-files (fleet) to json objects
#                           - shows information about the services it handles
#                           - talks to fleet (opens connection, publishes to fleet, add, removes services from fleet
class DynamiteServiceHandler(object):
    # Instance Variables
    DynamiteConfig = None
    FleetServiceDict = {}
    FleetServiceHandler = None

    # Takes a >> PATH/unit_file_name << as argument
    # Returns a python list-object (which can then be encoded to json)
    def unit2dict(self, unit_file_w_path):
        logging.info('Starting Converting Fleet-Unit File into Python-List')
        logging.info('File to be converted:' + unit_file_w_path)

        data = {}
        data["desiredState"] = None
        data["options"] = []

        with open(unit_file_w_path, 'r') as infile:
            section = ""
            multi_line_string = ""
            processing_mls = False

            for line in infile:

                line = line.strip()

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

                # This if-else statement parses multi-line strings
                if line[-1] == "\\":
                    string_wo_backslash = len(line) - 1
                    line = line[:string_wo_backslash]
                    if not processing_mls:
                        processing_mls = True
                        multi_line_string += line
                        continue
                    else:
                        multi_line_string += line
                        continue
                else:
                    if processing_mls:
                        multi_line_string += line
                        line = multi_line_string
                        processing_mls = False
                        multi_line_string = ""

                line = line.rstrip()
                name,value = line.split("=", 1)
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
        python_object = self.unit2dict(unit_file_w_path)
        json_object = json.dumps(python_object)
        return json_object


    # Takes a DynamiteConfig object which contains the name of the required service files as well as the paths where
    # those service files lie
    # Converts those service-files
    # Returns a dictionary containing json-objects of those service-files --> service-name --> json-object
    def dynamite_config_2_fleet_service_dict(self, dynamite_config):

        fleet_service_dict = {}

        if not isinstance(dynamite_config, DynamiteConfig):
            raise IllegalArgumentError("Error: Argument not instance of type 'DynamiteConfig'")

        service_dict = []

        for service_attributes in dynamite_config.Service.__dict__.values():
            service = {"service_name": service_attributes.name,
                       "name_of_unit_file": service_attributes.name_of_unit_file,
                       "service_details": service_attributes}

            service_dict.append(service)

        # key is name of the file, value is path of the file
        dict_of_files = {}

        # create a dictionary (file --> path) of the files contained in the folder in dynamite_config.ServiceFiles.PathList
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
        #for service in name_of_service_files:
        for service in service_dict:
            name_of_unit_file = service["name_of_unit_file"]
            if name_of_unit_file in dict_of_files:
                path_to_unit_file = dict_of_files[name_of_unit_file]
                #json_object = self.unit2json(path_to_unit_file)
                json_dict = self.unit2dict(path_to_unit_file)

                fleet_service = FleetService(service["service_name"],
                                             path_to_unit_file,
                                             json_dict,
                                             service["service_details"])

                fleet_service_dict[service["service_name"]] = fleet_service
            else:
                raise ServiceFileNotFoundError(name_of_unit_file + " Service-File was not found")

        return fleet_service_dict

    def submit_all_services_to_fleet(self, fleet_service_handler, fleet_service_dict):
        if not isinstance(fleet_service_handler, FleetServiceHandler):
            raise IllegalArgumentError("Error: Argument <FleetServiceHandler> not instance of type <dynamite.GENERAL.FleetServiceHandler")

        if not isinstance(fleet_service_dict, dict):
            pass

        # for service, fleet_service in fleet_service_dict.items():
        #     print(service)
        #     print(fleet_service)

    def __init__(self, dynamite_config):
        if not isinstance(dynamite_config, DynamiteConfig):
            raise IllegalArgumentError("Error: Argument not instance of type 'DynamiteConfig'")

        self.DynamiteConfig = dynamite_config

        self.FleetServiceDict = self.dynamite_config_2_fleet_service_dict(self.DynamiteConfig)

        self.FleetServiceHandler = FleetServiceHandler(dynamite_config.FleetAPIEndpoint.ip,
                                                       str(dynamite_config.FleetAPIEndpoint.port))

        self.submit_all_services_to_fleet(self.FleetServiceHandler, self.FleetServiceDict)

    def __str__(self):
        pass


if __name__ == '__main__':

    path_to_config_file = "..\\tests\\TEST_CONFIG_FOLDER\\config.yaml"
    service_folder_list = ['C:\\Users\\brnr\\PycharmProjects\\dynamite\\dynamite\\tests\\TEST_CONFIG_FOLDER\\service-files']

    dynamite_config = DynamiteConfig(path_to_config_file, service_folder_list)

    service_handler = DynamiteServiceHandler(dynamite_config)

    # for service_name, fleet_service_instance in service_handler.FleetServiceDict.items():
    #     print(fleet_service_instance.name)

    #print(service_handler.FleetServiceDict)

    #print(service_handler.ServiceJSONObjectDict['a_service_announcer@.service'])
    # this should be called from within the DynamiteServiceHandler!
    #fleet = FleetServiceHandler(dynamite_config.FleetAPIEndpoint.ip, str(dynamite_config.FleetAPIEndpoint.port))

    #fleet.submit('example.service', service_handler.ServiceJSONObjectDict['example.service'])
    #fleet.destroy('example.service')