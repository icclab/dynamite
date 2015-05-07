__author__ = 'brnr'

import os
import yaml


#from dynamite.INIT.DynamiteHelper import transform_dynamite_yaml_configuration_to_python_dict

class DynamiteConfig(object):
    # Instance Variables
    ServiceFiles = None
    FleetAPIEndpoint = None
    ETCD = None
    Service = None
    ScalingPolicy = None

    # config_file_name = "config.yaml"
    # config_file_directory = None
    # config_file_with_path = None

    class ServiceFilesStruct(object):
        # Instance Variables
        PathList = None

        def init_pathlist(self, PathList):
            checked_list_of_abs_paths = []

            for service_file_folder in PathList:
                if not os.path.isdir(service_file_folder):
                    raise NotADirectoryError("Error reading Dynamite Configuration (ServiceFiles-->PathList-->" + service_file_folder + " --> Is not a directory")
            if os.path.isabs(service_file_folder):
                checked_list_of_abs_paths.append(service_file_folder)
            else:
                checked_list_of_abs_paths.append(os.path.abspath(service_file_folder))

            return checked_list_of_abs_paths

        def __init__(self, PathList):
            self.PathList = self.init_pathlist(PathList) if len(PathList) != 0 else None

        def __str__(self):
            return "ServiceFiles Struct:\n" \
                   "\t<Instance Variables>\n" \
                   "\t\tPathList, type: List\n" \
                   "\t\t\tNumber of Entries: " + str(len(self.PathList))

    class FleetAPIEndpointStruct(object):
        # Instance Variables
        ip = None
        port = None

        def __init__(self, IP, Port):
            self.ip = IP
            self.port = Port

        def __str__(self):
            return "FleetAPIEndpoint Struct:\n" \
                   "\t<Instance Variables>\n" \
                   "\t\t<IP,\ttype: String>\n" \
                    "\t\t<Port,\ttype: Int>"

    class ETCDStruct(object):
        # Instance Variables
        ip_api_endpoint = None
        port_api_endpoint = None
        application_base_path = None

        def __init__(self, ip_api_endpoint, port_api_endpoint, application_base_path):
            self.ip_api_endpoint = ip_api_endpoint
            self.port_api_endpoint = port_api_endpoint
            self.application_base_path = application_base_path

        def __str__(self):
            return_string = "ETCD Struct:\n" \
                            "\t<Instance Variables>\n"

            for (instance_variable_name, value) in self.__dict__.items():
                return_string += "\t\tName: " + instance_variable_name + ", Type: " + str(type(value)) + "\n"

            return return_string

    class ServiceStruct(object):

        class ServiceDetailStruct(object):
            # Instance Variables
            name = None
            name_of_unit_file = None
            type = None
            min_instance = None
            max_instance = None
            base_instance_prefix_number = None
            service_announcer = None
            service_dependency = None
            scale_up_policy = None
            scale_down_policy = None

            def __init__(self, name, service_detail_dict):
                self.name = name
                self.name_of_unit_file = service_detail_dict['name_of_unit_file'] if 'name_of_unit_file' in service_detail_dict else None
                self.type = service_detail_dict['type'] if 'type' in service_detail_dict else None
                self.min_instance = service_detail_dict['min_instance'] if 'min_instance' in service_detail_dict else None
                self.max_instance = service_detail_dict['max_instance'] if 'max_instance' in service_detail_dict else None
                self.base_instance_prefix_number = service_detail_dict['base_instance_prefix_number'] if 'base_instance_prefix_number' in service_detail_dict else None
                self.service_announcer = service_detail_dict['service_announcer'] if 'service_announcer' in service_detail_dict else None
                self.service_dependency = service_detail_dict['service_dependency'] if 'service_dependency' in service_detail_dict else None
                self.scale_up_policy = service_detail_dict['scale_up_policy'] if 'scale_up_policy' in service_detail_dict else None
                self.scale_down_policy = service_detail_dict['scale_down_policy'] if 'scale_down_policy' in service_detail_dict else None

            def __str__(self):
                return_string = "ServiceDetail Struct:\n" \
                                "\t<Instance Variables>\n"

                for (instance_variable_name, value) in self.__dict__.items():
                    return_string += "\t\tName: " + instance_variable_name + ", Type: " + str(type(value)) + "\n"

                return return_string

        def __init__(self, ServicesDict):
            if(type(ServicesDict) == type({})):
                for (service_name, service_detail_dict) in ServicesDict.items():
                    setattr(self, service_name, DynamiteConfig.ServiceStruct.ServiceDetailStruct(service_name, service_detail_dict))

        def __str__(self):
            return_string = "Service Struct:\n" \
                            "\t<Instance Variables>\n"

            for (instance_variable_name, value) in self.__dict__.items():
                return_string += "\t\tName: " + instance_variable_name + ", Type: " + str(type(value)) + "\n"

            return return_string

    class ScalingPolicyStruct(object):

        class ScalingPolicyDetailStruct(object):
            # Instance Variables
            name = None
            service = None
            metric = None
            comparative_operator = None
            threshold = None
            threshold_unit = None
            period = None
            period_unit = None
            cooldown_period = None
            cooldown_period_unit = None

            def __init__(self, name, scaling_policy_detail_dict):
                    self.name = name
                    self.service = scaling_policy_detail_dict['service'] if 'service' in scaling_policy_detail_dict else None
                    self.metric = scaling_policy_detail_dict['metric'] if 'metric' in scaling_policy_detail_dict else None
                    self.comparative_operator = scaling_policy_detail_dict['comparative_operator'] if 'comparative_operator' in scaling_policy_detail_dict else None
                    self.threshold = scaling_policy_detail_dict['threshold'] if 'threshold' in scaling_policy_detail_dict else None
                    self.threshold_unit = scaling_policy_detail_dict['threshold_unit'] if 'threshold_unit' in scaling_policy_detail_dict else None
                    self.period = scaling_policy_detail_dict['period'] if 'period' in scaling_policy_detail_dict else None
                    self.period_unit = scaling_policy_detail_dict['period_unit'] if 'period_unit' in scaling_policy_detail_dict else None
                    self.cooldown_period = scaling_policy_detail_dict['cooldown_period'] if 'cooldown_period' in scaling_policy_detail_dict else None
                    self.cooldown_period_unit = scaling_policy_detail_dict['cooldown_period_unit'] if 'cooldown_period_unit' in scaling_policy_detail_dict else None

            def __str__(self):
                return_string = "ScalingPolicyDetail Struct:\n" \
                                "\t<Instance Variables>\n"

                for (instance_variable_name, value) in self.__dict__.items():
                    return_string += "\t\tName: " + instance_variable_name + ", Type: " + str(type(value)) + "\n"

                return return_string

        def __init__(self, ScalingPolicyDict):
            if(type(ScalingPolicyDict) == type({})):
                for (service_name, service_detail_dict) in ScalingPolicyDict.items():
                    setattr(self, service_name, DynamiteConfig.ScalingPolicyStruct.ScalingPolicyDetailStruct(service_name, service_detail_dict))

        def __str__(self):
            return_string = "ServicePolicy Struct:\n" \
                            "\t<Instance Variables>\n"

            for (instance_variable_name, value) in self.__dict__.items():
                return_string += "\t\tName: " + instance_variable_name + ", Type: " + str(type(value)) + "\n"

            return return_string

    # Converts YAML Config to Python Dictionary
    def load_config_file(self, path_to_config_file):

        with open(path_to_config_file, "r") as config_yaml:
            dynamite_yaml_config = yaml.load(config_yaml)

        return dynamite_yaml_config

    # The expected <dynamite_yaml_config> file is a Python List Object
    #def __init__(self, dynamite_yaml_config):
    def __init__(self, arg_config_path, arg_service_folder):

        dynamite_yaml_config = self.load_config_file(arg_config_path)

        self.dynamite_yaml_config = dynamite_yaml_config

        PathList = self.dynamite_yaml_config['Dynamite']['ServiceFiles']['PathList']
        self.ServiceFiles = DynamiteConfig.ServiceFilesStruct(PathList)

        # Combine the 2 lists containing paths to the service files
        if self.ServiceFiles.PathList != arg_service_folder:
            path_set_a = set(self.ServiceFiles.PathList)
            path_set_b = set(arg_service_folder)

            self.ServiceFiles.PathList = list(path_set_a)+list(path_set_b-path_set_a)

        IP = self.dynamite_yaml_config['Dynamite']['FleetAPIEndpoint']['ip']
        Port = self.dynamite_yaml_config['Dynamite']['FleetAPIEndpoint']['port']
        self.FleetAPIEndpoint = DynamiteConfig.FleetAPIEndpointStruct(IP,Port)

        etcd_ip_api_endpoint = self.dynamite_yaml_config['Dynamite']['ETCD']['ip_api_endpoint']
        etcd_port_api_endpoint = self.dynamite_yaml_config['Dynamite']['ETCD']['port_api_endpoint']
        etcd_application_base_path = self.dynamite_yaml_config['Dynamite']['ETCD']['application_base_path']
        self.ETCD = DynamiteConfig.ETCDStruct(etcd_ip_api_endpoint, etcd_port_api_endpoint, etcd_application_base_path)

        ServicesDict = self.dynamite_yaml_config['Dynamite']['Service']
        self.Service = DynamiteConfig.ServiceStruct(ServicesDict)

        ScalingPolicyDict = self.dynamite_yaml_config['Dynamite']['ScalingPolicy']
        self.ScalingPolicy = DynamiteConfig.ScalingPolicyStruct(ScalingPolicyDict)


# def transform_dynamite_yaml_configuration_to_python_dict(path_to_config_file=os.getcwd()):
#     if os.path.isdir(path_to_config_file):
#             config_file_directory = path_to_config_file
#             config_file_with_path = os.path.join(config_file_directory, "config.yaml")
#     else:
#         raise NotADirectoryError(path_to_config_file)
#
#     with open(config_file_with_path, "r") as config_yaml:
#         dynamite_yaml_config = yaml.load(config_yaml)
#
#     return dynamite_yaml_config


if __name__ == "__main__":

    path_to_config_file = "..\\tests\\TEST_CONFIG_FOLDER\\config.yaml"
    service_folder_list = ['C:\\Users\\brnr\\PycharmProjects\\dynamite\\dynamite\\tests\\TEST_CONFIG_FOLDER\\service-files']

    with open(path_to_config_file, "r") as dynamite_yaml_config_file:
        dynamite_yaml_config_dict = yaml.load(dynamite_yaml_config_file)

    dynamite_config = DynamiteConfig(path_to_config_file, service_folder_list)

    print(dynamite_config.Service.haproxy.type)

    #print(dynamite_config.FleetAPIEndpoint)
    #print(dynamite_config.Service)