__author__ = 'brnr'

import os
import yaml
import json

from intervaltree import Interval, IntervalTree
from dynamite.GENERAL.DynamiteExceptions import OverlappingPortRangeError
from dynamite.GENERAL.DynamiteExceptions import ServiceDependencyNotExistError
from dynamite.GENERAL import ETCDCTL

class DynamiteConfig(object):
    # Instance Variables
    ServiceFiles = None
    FleetAPIEndpoint = None
    ETCD = None
    Service = None
    ScalingPolicy = None

    IntervalTree = None         # Should not matter after initialization!

    dynamite_yaml_config = None

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
        # ip_api_endpoint = None
        # port_api_endpoint = None
        application_base_path = None
        metrics_base_path = None

        #def __init__(self, ip_api_endpoint, port_api_endpoint, application_base_path):
        def __init__(self, application_base_path, metrics_base_path):
            # self.ip_api_endpoint = ip_api_endpoint
            # self.port_api_endpoint = port_api_endpoint
            self.application_base_path = application_base_path
            self.metrics_base_path = metrics_base_path

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
            ports_per_instance = None
            service_announcer = None
            service_dependency = None
            scale_up_policy = None
            scale_down_policy = None

            def to_dict(self):
                service_detail_json = {}

                for key, value in self.__dict__.items():
                    service_detail_json[key] = value

                return service_detail_json

            @staticmethod
            def dict_to_instance(service_detail_struct_dict):

                name = service_detail_struct_dict['name']

                del service_detail_struct_dict['name']

                service_detail_struct_instance = DynamiteConfig.ServiceStruct.ServiceDetailStruct(name,
                                                                                                  service_detail_struct_dict)

                return service_detail_struct_instance

            def __init__(self, name, service_detail_dict):
                self.name = name
                self.name_of_unit_file = service_detail_dict['name_of_unit_file'] if 'name_of_unit_file' in service_detail_dict else None
                self.type = service_detail_dict['type'] if 'type' in service_detail_dict else None
                self.min_instance = service_detail_dict['min_instance'] if 'min_instance' in service_detail_dict else None
                self.max_instance = service_detail_dict['max_instance'] if 'max_instance' in service_detail_dict else None
                self.base_instance_prefix_number = service_detail_dict['base_instance_prefix_number'] if 'base_instance_prefix_number' in service_detail_dict else None
                self.ports_per_instance = service_detail_dict['ports_per_instance'] if 'ports_per_instance' in service_detail_dict else None
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

            def __repr__(self):
                return "ServiceDetailStruct(name={},name_of_unit_file={},type={},min_instance={},max_instance={}," \
                       "base_instance_prefix_number={},service_announcer={},service_dependency={}," \
                       "scale_up_policy={},scale_down_policy={})".format(
                            self.name,
                            self.name_of_unit_file,
                            self.type,
                            repr(self.min_instance),
                            repr(self.max_instance),
                            repr(self.base_instance_prefix_number),
                            repr(self.service_announcer),
                            repr(self.service_dependency),
                            repr(self.scale_up_policy),
                            repr(self.scale_down_policy)
                )

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
            service_type = None
            metric = None
            metric_aggregated = None
            comparative_operator = None
            threshold = None
            threshold_unit = None
            period = None
            period_unit = None
            cooldown_period = None
            cooldown_period_unit = None

            def __init__(self, name, scaling_policy_detail_dict):
                    self.name = name
                    self.service_type = scaling_policy_detail_dict['service_type'] if 'service_type' in scaling_policy_detail_dict else None
                    self.metric = scaling_policy_detail_dict['metric'] if 'metric' in scaling_policy_detail_dict else None
                    self.metric_aggregated = scaling_policy_detail_dict['metric_aggregated'] if 'metric_aggregated' in scaling_policy_detail_dict else None
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
                    setattr(
                        self,
                        service_name,
                        DynamiteConfig.ScalingPolicyStruct.ScalingPolicyDetailStruct(service_name, service_detail_dict)
                    )

        def __str__(self):
            return_string = "ServicePolicy Struct:\n" \
                            "\t<Instance Variables>\n"

            for (instance_variable_name, value) in self.__dict__.items():
                return_string += "\t\tName: " + instance_variable_name + ", Type: " + str(type(value)) + "\n"

            return return_string

        # do not make a property out of this, this would break the logic creating variables for each policy
        def get_scaling_policies(self):
            scaling_policies = []
            for (instance_variable_name, value) in self.__dict__.items():
                scaling_policies.append(value)
            return scaling_policies

    # Converts YAML Config to Python Dictionary
    def load_config_file(self, path_to_config_file):

        with open(path_to_config_file, "r") as config_yaml:
            dynamite_yaml_config = yaml.load(config_yaml)

        return dynamite_yaml_config

    def check_for_overlapping_port_ranges(self):
        self.IntervalTree = IntervalTree()

        for service_name, service_detail in self.Service.__dict__.items():
            if service_detail.base_instance_prefix_number is not None:
                interval_start = service_detail.base_instance_prefix_number
                interval_end = interval_start + service_detail.max_instance
                new_interval = Interval(interval_start, interval_end)

                # True if <new_interval> is already contained in interval
                if sorted(self.IntervalTree[new_interval]):
                    raise OverlappingPortRangeError("Error: " + new_interval + " overlaps with already existing interval(s)"
                                                    + sorted(self.IntervalTree[new_interval]))
                else:
                    self.IntervalTree.add(new_interval)

    # check for existence of service_dependencies
    def check_for_service_dependencies(self):
        list_of_services = []

        for service_name in self.Service.__dict__.keys():
            list_of_services.append(service_name)

        for service_detail in self.Service.__dict__.values():
            if service_detail.service_dependency is not None:
                for service_dependency in service_detail.service_dependency:
                    if service_dependency not in list_of_services:
                        raise ServiceDependencyNotExistError("Error: Service <" + service_dependency +
                                                             "> defined as service dependency of service <" +
                                                             service_detail.name +
                                                             "> was not found in list of defined services --> " +
                                                             str(list_of_services))

    def set_instance_variables(self, dynamite_yaml_config, arg_service_folder_list=None):

        self.dynamite_yaml_config = dynamite_yaml_config

        if isinstance(arg_service_folder_list, str):
            tmp_str = arg_service_folder_list
            arg_service_folder_list = []
            arg_service_folder_list.append(tmp_str)

        PathList = self.dynamite_yaml_config['Dynamite']['ServiceFiles']['PathList']
        self.ServiceFiles = DynamiteConfig.ServiceFilesStruct(PathList)

        # Combine the 2 lists containing paths to the service files
        if arg_service_folder_list:
            if self.ServiceFiles.PathList != arg_service_folder_list:
                path_set_a = set(self.ServiceFiles.PathList)
                path_set_b = set(arg_service_folder_list)

                self.ServiceFiles.PathList = list(path_set_a)+list(path_set_b-path_set_a)

        # check if Folders in ServiceFiles-->PathList exit
        for folder in self.ServiceFiles.PathList:
            if not os.path.isdir(folder):
                raise NotADirectoryError("Error: " + folder + " is not a valid directory")

        IP = self.dynamite_yaml_config['Dynamite']['FleetAPIEndpoint']['ip']
        Port = self.dynamite_yaml_config['Dynamite']['FleetAPIEndpoint']['port']
        self.FleetAPIEndpoint = DynamiteConfig.FleetAPIEndpointStruct(IP,Port)

        etcd_application_base_path = self.dynamite_yaml_config['Dynamite']['ETCD']['application_base_path']
        etcd_metrics_base_path = self.dynamite_yaml_config['Dynamite']['ETCD']['metrics_base_path']
        self.ETCD = DynamiteConfig.ETCDStruct(etcd_application_base_path, etcd_metrics_base_path)

        ServicesDict = self.dynamite_yaml_config['Dynamite']['Service']
        self.Service = DynamiteConfig.ServiceStruct(ServicesDict)

        ScalingPolicyDict = self.dynamite_yaml_config['Dynamite']['ScalingPolicy']
        self.ScalingPolicy = DynamiteConfig.ScalingPolicyStruct(ScalingPolicyDict)

    def init_from_file(self, arg_config_path=None, arg_service_folder_list=None):
        # Test if Config-File exists. If not, terminate application
        if not os.path.exists(arg_config_path):
            raise FileNotFoundError("--config-file: " + arg_config_path + " --> File at given config-path does not exist")
        else:
            dynamite_yaml_config = self.load_config_file(arg_config_path)

        self.set_instance_variables(dynamite_yaml_config, arg_service_folder_list)

    def init_from_etcd(self, etcd_endpoint):

        etcdctl = ETCDCTL.create_etcdctl(etcd_endpoint)

        if etcdctl is not None:
            res = etcdctl.read(ETCDCTL.etcd_key_init_application_configuration)
            dynamite_config_str = res.value

            if dynamite_config_str is not None and isinstance(dynamite_config_str, str):
                dynamite_yaml_config = json.loads(dynamite_config_str)
                self.set_instance_variables(dynamite_yaml_config)

        else:
            return None

    # Arguments:    arg_config_path: Path to the Dynamite YAML config file
    #               arg_service_folder (Optional):  List of paths containing service-files.
    #                                               Can also/additionally be defined in the dynamite yaml configuration file
    def __init__(self, arg_config_path=None, arg_service_folder_list=None, etcd_endpoint=None):

        if arg_config_path is not None:
            self.init_from_file(arg_config_path, arg_service_folder_list)

        if etcd_endpoint is not None:
            self.init_from_etcd(etcd_endpoint)



if __name__ == "__main__":

    path_to_config_file = "..\\tests\\TEST_CONFIG_FOLDER\\config.yaml"
    #service_folder_list = 'path\\to\\nowhere'
    service_folder_list = "..\\tests\\TEST_CONFIG_FOLDER"

    #service_folder_list = ['C:\\Users\\brnr\\PycharmProjects\\dynamite\\dynamite\\tests\\TEST_CONFIG_FOLDER\\service-files']

    dynamite_config = DynamiteConfig(path_to_config_file, service_folder_list)

    for service_policy_name, scaling_policy in dynamite_config.ScalingPolicy.__dict__.items():
        print(scaling_policy.service)

    #dynamite_config = DynamiteConfig(path_to_config_file)
    #dynamite_config = DynamiteConfig("/it/is/just/wrong.yaml")

    #print(dynamite_config.Service.a)

    #print(dynamite_config.FleetAPIEndpoint)
    #print(dynamite_config.Service)