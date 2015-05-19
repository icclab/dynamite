__author__ = 'brnr'

import json
import os
import logging

from dynamite.GENERAL.DynamiteExceptions import IllegalArgumentError
from dynamite.GENERAL.DynamiteExceptions import ServiceFileNotFoundError
from dynamite.GENERAL.DynamiteExceptions import DuplicateServiceFileError
from dynamite.GENERAL.DynamiteExceptions import ServiceAnnouncerFileNotFoundError
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

        # Collect necessary information of services defined in 'config.yaml' file and save them in 'service_dict' dictionary
        service_dict = {}
        for service_attributes in dynamite_config.Service.__dict__.values():
            service_dict[service_attributes.name] = {"service_name": service_attributes.name,
                                                     "name_of_unit_file": service_attributes.name_of_unit_file,
                                                     "service_details": service_attributes}

        # Create a dictionary (file --> path) of the files contained in the folder in dynamite_config.ServiceFiles.PathList
        dict_of_files = {}
        for service_file_folder in dynamite_config.ServiceFiles.PathList:
            list_of_files = os.listdir(service_file_folder)

            for file in list_of_files:
                abs_path_of_file = os.path.join(service_file_folder, file)
                if os.path.isfile(abs_path_of_file):
                    if file in dict_of_files:
                        raise DuplicateServiceFileError("Error: " + file + " was found 2 times")
                    else:
                        dict_of_files[file] = abs_path_of_file

        # Go through all the services defined in the dynamite configuration (Dynamite.Service.<x>)
        #
        # Raises an error if any 'Dynamite.Service.<ServiceName>.name_of_unit_file' does not exists in any of the
        # paths defined in 'Dynamite.ServiceFiles.PathList
        #
        # If the file exits a new FleetService gets created
        #   If the file/service uses a 'Service_Announcer' a FleetService for the Service_Announcer gets created and
        #   attached to the 'original/parent' FleetService
        for service_name, service_info_dict in service_dict.items():

            name_of_unit_file = service_info_dict["name_of_unit_file"]

            if name_of_unit_file in dict_of_files and service_info_dict["service_details"].type != "service_announcer":

                service_details = service_info_dict["service_details"]
                path_to_unit_file = dict_of_files[name_of_unit_file]
                json_dict = self.unit2dict(path_to_unit_file)

                # print(service_details.name)
                # print(service_details.name_of_unit_file)

                service_is_template = True if "@" in service_details.name_of_unit_file else False
                service_announcer_fleet_service = None

                if service_details.service_announcer:
                    service_announcer_name = service_details.service_announcer
                    service_announcer_details = getattr(dynamite_config.Service, service_announcer_name)
                    name_of_service_announcer_unit_file = service_announcer_details.name_of_unit_file

                    if name_of_service_announcer_unit_file in dict_of_files:
                        service_announcer_is_template = True if "@" in service_details.name_of_unit_file else False
                        path_to_service_announcer_unit_file = dict_of_files[name_of_service_announcer_unit_file]
                        service_announcer_json_dict = self.unit2dict(path_to_service_announcer_unit_file)

                        service_announcer_fleet_service = FleetService(service_announcer_name,
                                                                       path_to_service_announcer_unit_file,
                                                                       service_announcer_json_dict,
                                                                       service_announcer_details,
                                                                       state=None,
                                                                       is_template=service_announcer_is_template,
                                                                       service_announcer=None
                                                                       )
                    else:
                        raise ServiceAnnouncerFileNotFoundError("Error: <" + name_of_service_announcer_unit_file + "> File was not found.")

                fleet_service = FleetService(service_name,
                                             path_to_unit_file,
                                             json_dict,
                                             service_details,
                                             None,
                                             service_is_template,
                                             service_announcer_fleet_service)

                fleet_service_dict[service_info_dict["service_name"]] = fleet_service
            elif service_info_dict["service_details"].type == "service_announcer":
                pass
            else:
                raise ServiceFileNotFoundError(name_of_unit_file + " Service-File was not found")

        return fleet_service_dict

    def _initial_start_all_services_to_fleet(self, fleet_service_handler, fleet_service_dict):
        if not isinstance(fleet_service_handler, FleetServiceHandler):
            raise IllegalArgumentError("Error: Argument <FleetServiceHandler> not instance of type <dynamite.GENERAL.FleetServiceHandler")

        # TODO: Create in the minimum as many services as defined by 'min_instance'
        #       If service is not a template just create one instance
        for service_name, fleet_service in fleet_service_dict.items():
            if fleet_service.service_config_details.min_instance:
                min_instances = fleet_service.service_config_details.min_instance
            else:
                min_instances = 1

            for times in range(min_instances):
                fleet_service_instance = fleet_service_handler.create_new_fleet_service_instance(fleet_service)
                fleet_service_handler.submit(fleet_service_instance)
                fleet_service_handler.start(fleet_service_instance)

    def destroy_all_services(self):
        fleet_service_handler = self.FleetServiceHandler
        fleet_service_dict = self.FleetServiceDict

        for service_name, fleet_service in fleet_service_dict.items():
            for instance_name, instance_fleet_service in fleet_service.fleet_service_instances.items():
                fleet_service_handler.destroy(instance_fleet_service)

    def add_new_fleet_service_instance(self, fleet_service_name):
        if not isinstance(fleet_service_name, str):
            raise IllegalArgumentError("Error: Argument <fleet_service_name> not of type <str>")

        if fleet_service_name in self.FleetServiceDict:

            fleet_service = self.FleetServiceDict[fleet_service_name]
            new_fleet_service_instance = self.FleetServiceHandler.create_new_fleet_service_instance(fleet_service)

            if new_fleet_service_instance is not None:
                self.FleetServiceHandler.start(new_fleet_service_instance)
        else:
            return None

    def remove_fleet_service_instance(self, fleet_service_instance_name):
        fleet_service_handler = self.FleetServiceHandler
        fleet_service_dict = self.FleetServiceDict

        for service_name, fleet_service in fleet_service_dict.items():
            if fleet_service_instance_name in fleet_service.fleet_service_instances:
                # return fleet_service_handler.destroy(fleet_service.fleet_service_instances[fleet_service_instance_name])
                return fleet_service_handler.remove_fleet_service_instance(fleet_service, fleet_service_instance_name)

        return None

    def __init__(self, dynamite_config):
        if not isinstance(dynamite_config, DynamiteConfig):
            raise IllegalArgumentError("Error: Argument <dynamite_config> not instance of type 'DynamiteConfig'")

        self.DynamiteConfig = dynamite_config

        self.FleetServiceDict = self.dynamite_config_2_fleet_service_dict(self.DynamiteConfig)

        self.FleetServiceHandler = FleetServiceHandler(dynamite_config.FleetAPIEndpoint.ip,
                                                       str(dynamite_config.FleetAPIEndpoint.port))

        self._initial_start_all_services_to_fleet(self.FleetServiceHandler, self.FleetServiceDict)



    def __str__(self):
        pass


if __name__ == '__main__':

    path_to_config_file = "..\\tests\\TEST_CONFIG_FOLDER\\config.yaml"
    service_folder_list = ['C:\\Users\\brnr\\PycharmProjects\\dynamite\\dynamite\\tests\\TEST_CONFIG_FOLDER\\service-files']

    dynamite_config = DynamiteConfig(path_to_config_file, service_folder_list)

    service_handler = DynamiteServiceHandler(dynamite_config)

    service_handler.add_new_fleet_service_instance("a")

    # print(service_handler.FleetServiceDict)
    # print(service_handler.FleetServiceDict['a'].fleet_service_instances["a@12021.service"])
    # print(service_handler.FleetServiceDict['a'].fleet_service_instances["a@12021.service"].state)

    # for service_name, fleet_service_instance in service_handler.FleetServiceDict.items():
    #     print(service_name)
    #     print(fleet_service_instance.service_config_details.name_of_unit_file)

    #print(service_handler.FleetServiceDict)

    #print(service_handler.ServiceJSONObjectDict['a_service_announcer@.service'])
    # this should be called from within the DynamiteServiceHandler!
    #fleet = FleetServiceHandler(dynamite_config.FleetAPIEndpoint.ip, str(dynamite_config.FleetAPIEndpoint.port))

    #fleet.submit('example.service', service_handler.ServiceJSONObjectDict['example.service'])
    #fleet.destroy('example.service')