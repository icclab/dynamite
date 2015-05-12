__author__ = 'brnr'

import os
from dynamite.INIT.DynamiteConfig import DynamiteConfig


class FLEET_STATE_STRUCT(object):
    INACTIVE = "inactive"
    LOADED = "loaded"
    LAUNCHED = "launched"
    ALLOWED_STATES = ["inactive", "loaded", "launched"]


class FleetService(object):
    name = None
    path_on_filesystem = None
    unit_file_details_json_dict = None
    state = None
    service_config_details = None               # of type DynamiteConfig.ServiceStruct.ServiceDetailStruct

    def __init__(self,
                 name,
                 path_on_filesystem,
                 unit_file_details_json_dict,
                 service_details_dynamite_config,
                 state=None):

        # add a check for the variables (if None, path exists, etc)
        self.name = name
        self.unit_file_details_json_dict = unit_file_details_json_dict
        self.state = state

        if not os.path.exists(path_on_filesystem):
            raise FileNotFoundError("Error: <" + path_on_filesystem + "> does not exist")
        else:
            self.path_on_filesystem = path_on_filesystem

        if not isinstance(service_details_dynamite_config, DynamiteConfig.ServiceStruct.ServiceDetailStruct):
            raise ValueError("Error: <service_details> argument needs to be of type <DynamiteConfig.ServiceStruct.ServiceDetailStruct>")
        else:
            self.service_config_details = service_details_dynamite_config

    def __str__(self):
        return_string = "FleetService Instance:\n" \
                        "\t<Instance Variables>\n"

        for (instance_variable_name, value) in self.__dict__.items():
            return_string += "\t\tName: " + instance_variable_name + ", Type: " + str(type(value)) + "\n"

        return return_string


if __name__ == '__main__':
    print(type(FLEET_STATE_STRUCT.INACTIVE))