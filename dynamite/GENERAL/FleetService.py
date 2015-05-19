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
    service_config_details = None           # of type DynamiteConfig.ServiceStruct.ServiceDetailStruct
    is_template = None
    used_port_numbers = None
    service_announcer = None

    fleet_service_instances = None

    def get_next_port_numbers(self):
        if self.is_template is None:
            return None

        if self.used_port_numbers is None:
            return None

        # All ports already used
        if 0 not in self.used_port_numbers:
            return None

        next_ports_to_use = []
        ports_per_instance = self.service_config_details.ports_per_instance
        base_port_number = self.service_config_details.base_instance_prefix_number

        for i in range(ports_per_instance):
            port_number = base_port_number + self.used_port_numbers.index(0)
            self.used_port_numbers[self.used_port_numbers.index(0)] = port_number
            next_ports_to_use.append(port_number)

        return next_ports_to_use

    def __init__(self,
                 name,
                 path_on_filesystem,
                 unit_file_details_json_dict,
                 service_details_dynamite_config,
                 state=None,
                 is_template=None,
                 service_announcer=None):

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

        if is_template is None:
            self.is_template = False
        else:
            self.is_template = is_template

        if is_template and self.service_config_details.type != "service_announcer":
            self.used_port_numbers = [0] * self.service_config_details.max_instance * self.service_config_details.ports_per_instance

        if service_announcer is not None:
            self.service_announcer = service_announcer

        self.fleet_service_instances = {}

    def __str__(self):
        return_string = "FleetService Instance:\n" \
                        "\t<Instance Variables>\n"

        for (instance_variable_name, value) in self.__dict__.items():
            return_string += "\t\tName: " + instance_variable_name + ", Type: " + str(type(value)) + "\n"

        return return_string


if __name__ == '__main__':
    print(type(FLEET_STATE_STRUCT.INACTIVE))