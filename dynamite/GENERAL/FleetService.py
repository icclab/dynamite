__author__ = 'brnr'

import os
from dynamite.INIT.DynamiteConfig import DynamiteConfig


class FLEET_STATE_STRUCT(object):
    INACTIVE = "inactive"
    LOADED = "loaded"
    LAUNCHED = "launched"
    ALLOWED_STATES = [None, "inactive", "loaded", "launched"]

class FleetService(object):
    name = None
    path_on_filesystem = None
    unit_file_details_json_dict = None
    service_config_details = None           # of type DynamiteConfig.ServiceStruct.ServiceDetailStruct
    is_template = None
    used_port_numbers = None

    attached_services = None

    fleet_service_instances = None

    def __init__(self,
                 name,
                 path_on_filesystem=None,
                 unit_file_details_json_dict=None,
                 service_details_dynamite_config=None,
                 is_template=None,
                 attached_services=None,
                 used_port_numbers=None):

        # add a check for the variables (if None, path exists, etc)
        self.name = name
        self.unit_file_details_json_dict = unit_file_details_json_dict

        if path_on_filesystem is not None:
            if not os.path.exists(path_on_filesystem):
                raise FileNotFoundError("Error: <" + path_on_filesystem + "> does not exist")
            else:
                self.path_on_filesystem = path_on_filesystem
        else:
            self.path_on_filesystem = None

        if service_details_dynamite_config is not None:
            if not isinstance(service_details_dynamite_config, DynamiteConfig.ServiceStruct.ServiceDetailStruct):
                raise ValueError("Error: <service_details> argument needs to be of type <DynamiteConfig.ServiceStruct.ServiceDetailStruct>")
            else:
                self.service_config_details = service_details_dynamite_config
        else:
            self.service_config_details = None

        if is_template is None:
            self.is_template = False
        else:
            self.is_template = is_template

        if is_template and self.service_config_details.type != "service_announcer":
            if used_port_numbers is not None:
                self.used_port_numbers = used_port_numbers
            else:
                self.used_port_numbers = [0] * self.service_config_details.max_instance * self.service_config_details.ports_per_instance

        if attached_services is not None:
            self.attached_services = attached_services
        else:
            self.attached_services = []

        self.fleet_service_instances = {}

    def has_attached_services(self):
            is_not_none = self.attached_services is not None
            has_at_least_one_attached_service = len(self.attached_services) > 0
            return is_not_none and has_at_least_one_attached_service

    def to_dict(self):
        fleet_service_json = {}

        for key, value in self.__dict__.items():
            if key == "service_config_details" and value is not None:
                service_config_details_json = value.to_dict()
                fleet_service_json[key] = service_config_details_json
            elif key == "attached_services":
                if value is not None:
                    attached_services_json = []
                    for attached_service in value:
                        fleet_service_announcer_json = attached_service.to_dict()
                        attached_services_json.append(fleet_service_announcer_json)
                    fleet_service_json[key] = attached_services_json
                else:
                    fleet_service_json[key] = None
            elif key == "fleet_service_instances":
                if len(value) != 0:
                    # fleet_service_json[key] = value
                    fleet_service_instances_json = {}

                    for service_instance_key, service_instance_value in value.items():
                        service_instance_json = service_instance_value.to_dict()
                        fleet_service_instances_json[service_instance_key] = service_instance_json

                    fleet_service_json[key] = fleet_service_instances_json
                else:
                    fleet_service_json[key] = None
            else:
                fleet_service_json[key] = value

        return fleet_service_json

    @staticmethod
    def dict_to_instance(fleet_service_dict):

        attached_services = []
        if 'attached_services'in fleet_service_dict:
            attached_services_dict = fleet_service_dict['attached_services']
            for attached_service_name in attached_services_dict:
                attached_services.append(FleetService.dict_to_instance(attached_service_name))

        service_config_details = DynamiteConfig.ServiceStruct.ServiceDetailStruct.dict_to_instance(
            fleet_service_dict['service_config_details'])

        if 'used_port_numbers' in fleet_service_dict:
            used_port_numbers = fleet_service_dict['used_port_numbers']
        else:
            used_port_numbers = None

        fleet_service_instance = FleetService(fleet_service_dict['name'],
                                              path_on_filesystem=fleet_service_dict['path_on_filesystem'],
                                              unit_file_details_json_dict=fleet_service_dict['unit_file_details_json_dict'],
                                              service_details_dynamite_config=service_config_details,
                                              is_template=fleet_service_dict['is_template'],
                                              attached_services=attached_services,
                                              used_port_numbers=used_port_numbers)

        return fleet_service_instance

    def get_next_port_numbers(self):
        if self.is_template is None:
            return None

        if self.used_port_numbers is None:
            return None

        # All ports already used
        if 0 not in self.used_port_numbers:
            return -1

        next_ports_to_use = []
        ports_per_instance = self.service_config_details.ports_per_instance
        base_port_number = self.service_config_details.base_instance_prefix_number

        for i in range(ports_per_instance):
            port_number = base_port_number + self.used_port_numbers.index(0)
            self.used_port_numbers[self.used_port_numbers.index(0)] = port_number
            next_ports_to_use.append(port_number)

        return next_ports_to_use

    def __str__(self):
        return_string = "FleetService Instance:\n" \
                        "\t<Instance Variables>\n"

        for (instance_variable_name, value) in self.__dict__.items():
            return_string += "\t\tName: " + instance_variable_name + ", Type: " + str(type(value)) + "\n"

        return return_string

    def __repr__(self):
        return "FleetService(name={},path_on_filesystem={},service_config_details={},is_template={}," \
               "used_port_numbers={},attached_services={},service_instances={})".format(
                    self.name,
                    self.path_on_filesystem,
                    repr(self.service_config_details),
                    repr(self.is_template),
                    repr(self.used_port_numbers),
                    repr(self.attached_services),
                    repr(self.fleet_service_instances)
               )

    class FleetServiceInstance(object):
        # instance name like service_name@port.service
        name = None
        state = None

        attached_services = None

        # expected type of attached_services FleetService.FleetServiceInstance[]
        def __init__(self, name, state, attached_services=None):
            self.name = name

            if state in FLEET_STATE_STRUCT.ALLOWED_STATES:
                self.state = state
            else:
                raise ValueError("Error state needs to one of these: " + str(FLEET_STATE_STRUCT.ALLOWED_STATES))

            self.attached_services = []
            if attached_services is not None:
                self.attached_services = attached_services

        def has_attached_services(self):
            is_not_none = self.attached_services is not None
            has_at_least_one_attached_service = len(self.attached_services) > 0
            return is_not_none and has_at_least_one_attached_service

        def to_dict(self):
            fleet_service_json = {}

            for key, value in self.__dict__.items():
                if key == "attached_services":
                    if value is not None:
                        attached_services = []
                        for attached_service in value:
                            attached_service_json = attached_service.to_dict()
                            attached_services.append(attached_service_json)
                        fleet_service_json[key] = attached_services
                    else:
                        fleet_service_json[key] = []
                else:
                    fleet_service_json[key] = value

            return fleet_service_json

        @staticmethod
        def dict_to_instance(fleet_service_instance_dict):
            attached_services = []
            if 'attached_service' in fleet_service_instance_dict:
                attached_services_dict = fleet_service_instance_dict['attached_service']
                for attached_service_dict in attached_services_dict:
                    attached_service = FleetService.FleetServiceInstance.dict_to_instance(attached_service_dict)
                    attached_services.append(attached_service)

            fleet_service_instance = FleetService.FleetServiceInstance(name=fleet_service_instance_dict['name'],
                                                                       state=fleet_service_instance_dict['state'],
                                                                       attached_services=attached_services)

            return fleet_service_instance

        def __str__(self):
            return_string = "FleetServiceInstance Instance:\n" \
                            "\t<Instance Variables>\n"

            for (instance_variable_name, value) in self.__dict__.items():
                return_string += "\t\tName: " + instance_variable_name + ", Type: " + str(type(value)) + "\n"

            return return_string

        def __repr__(self):
            return "FleetServiceInstance(name={},state={},attached_services={})".format(
                self.name,
                repr(self.state),
                repr(self.attached_services)
            )

