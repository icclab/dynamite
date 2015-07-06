__author__ = 'brnr'

import yaml
import pytest
import os

from dynamite.INIT.DynamiteConfig import DynamiteConfig

absolute_path_of_service_folder = os.path.abspath('tests\\TEST_CONFIG_FOLDER\\service-files')

@pytest.fixture(scope="module")
def path_to_tmp_dynamite_config_file(request):

    name_of_tmp_config_file = "tmp_test_dynamite_config.yaml"
    path_to_tmp_config_file = "tests\\INIT"

    tmp_config_file = os.path.join(path_to_tmp_config_file, name_of_tmp_config_file)

    dynamite_yaml_test_config_dict = \
        {
            'Dynamite': {
                'ServiceFiles': {
                    'PathList': [absolute_path_of_service_folder]
                },
                'FleetAPIEndpoint': {
                    'ip': '172.17.8.101',
                    'port': 49153
                },
                'ETCD': {
                    'ip_api_endpoint': '127.0.0.1',
                    'port_api_endpoint': 4001,
                    'application_base_path': '/services',
                    'metrics_base_path': "/metrics"
                },
                'Service': {
                    'apache': {
                        'name_of_unit_file': 'apache@.service',
                        'type': 'webserver',
                        'min_instance': 2,
                        'max_instance': 5,
                        'base_instance_prefix_number': 8080,
                        'service_announcer': 'zurmo_apache_discovery',
                        'service_dependency': ['zurmo_application', 'zurmo_config'],
                        'scale_up_policy': {
                            'ScalingPolicy': 'scale_up'
                        },
                        'scale_down_policy': {
                            'ScalingPolicy': 'scale_down'
                        }
                    },
                    'haproxy': {
                        'name_of_unit_file': 'haproxy.service',
                        'type': 'loadbalancer',
                        'min_instance': 1,
                        'max_instance': 1,
                        'base_instance_prefix_number': 80,
                        'service_announcer': 'zurmo_haproxy_discovery'
                    }
                },
                'ScalingPolicy': {
                    'scale_up': {
                        'service_type': 'haproxy',
                        'metric': 'response_time',
                        'comparative_operator': 'gt',
                        'threshold': 250,
                        'treshold_unit': 'micro_second',
                        'period': 15,
                        'period_unit': 'second',
                        'cooldown_period': 1,
                        'cooldown_period_unit': 'minute',
                    },
                    'scale_down': {
                        'service_type': 'apache',
                        'metric': 'cpu_load',
                        'comparative_operator': 'lt',
                        'threshold': 30,
                        'threshold_unit': 'percent',
                        'period': 30,
                        'period_unit': 'second',
                        'cooldown_period': 1,
                        'cooldown_period_unit': 'minute',
                    }
                }
            }
        }

    dynamite_config_yaml = yaml.dump(dynamite_yaml_test_config_dict)

    with open(tmp_config_file, "w") as tmp_yaml_config_file:
            tmp_yaml_config_file.write(dynamite_config_yaml)

    @request.addfinalizer
    def teardown():
        tmp_yaml_config_file.close()
        os.remove(tmp_config_file)

    cwd = os.path.abspath(os.path.dirname(__file__))
    path_to_tmp_config = os.path.join(cwd, name_of_tmp_config_file)

    return path_to_tmp_config

def test_create_dynamiteConfig_object_with_arg_config_path_argument(path_to_tmp_dynamite_config_file):
    arg_config_path = path_to_tmp_dynamite_config_file

    dynamite_config = DynamiteConfig(arg_config_path=arg_config_path)
    assert dynamite_config

def test_create_dynamiteConfig_with_incorrect_arg_config_path_argument():
    arg_config_path = "/just/plain/wrong.yaml"

    with pytest.raises(FileNotFoundError):
        dynamite_config = DynamiteConfig(arg_config_path)

def test_create_dynamiteConfig_object_with_arg_config_path_and_arg_service_folder_list_argument(path_to_tmp_dynamite_config_file):
    arg_config_path = path_to_tmp_dynamite_config_file
    arg_service_folder_list = ['tests\\TEST_CONFIG_FOLDER\\service-files']

    dynamite_config = DynamiteConfig(arg_config_path, arg_service_folder_list)
    assert dynamite_config

    path_list = dynamite_config.ServiceFiles.PathList

    assert len(path_list) == 2
    assert 'tests\\TEST_CONFIG_FOLDER\\service-files' in path_list
    assert absolute_path_of_service_folder in path_list

def test_create_dynamiteConfig_object_with_arg_service_folder_list_argument_same_value_as_in_config(path_to_tmp_dynamite_config_file):
    arg_config_path = path_to_tmp_dynamite_config_file
    arg_service_folder_list = [absolute_path_of_service_folder]

    dynamite_config = DynamiteConfig(arg_config_path, arg_service_folder_list)
    assert dynamite_config

    path_list = dynamite_config.ServiceFiles.PathList

    assert len(path_list) == 1
    assert absolute_path_of_service_folder in path_list

def test_create_dynamiteConfig_object_with_arg_service_folder_list_argument_with_multiple_duplicate_values(path_to_tmp_dynamite_config_file):
    arg_config_path = path_to_tmp_dynamite_config_file
    arg_service_folder_list = [absolute_path_of_service_folder, 'tests\\TEST_CONFIG_FOLDER\\service-files']

    dynamite_config = DynamiteConfig(arg_config_path, arg_service_folder_list)
    assert dynamite_config

    path_list = dynamite_config.ServiceFiles.PathList

    assert len(path_list) == 2
    assert 'tests\\TEST_CONFIG_FOLDER\\service-files' in path_list
    assert absolute_path_of_service_folder in path_list

def test_create_dynamiteConfig_object_with_arg_service_folder_list_argument_containing_incorrect_value(path_to_tmp_dynamite_config_file):
    arg_config_path = path_to_tmp_dynamite_config_file
    arg_service_folder_list = ['path\\to\\nowhere']

    with pytest.raises(NotADirectoryError):
        dynamite_config = DynamiteConfig(arg_config_path, arg_service_folder_list)

def test_create_dynamiteConfig_object_with_arg_service_folder_list_argument_containing_incorrect_string_value(path_to_tmp_dynamite_config_file):
    arg_config_path = path_to_tmp_dynamite_config_file
    arg_service_folder_list = 'path\\to\\nowhere'

    with pytest.raises(NotADirectoryError):
        dynamite_config = DynamiteConfig(arg_config_path, arg_service_folder_list)

def test_create_dynamiteConfig_object_with_arg_service_folder_list_argument_containing_correct_string_value(path_to_tmp_dynamite_config_file):
    arg_config_path = path_to_tmp_dynamite_config_file
    arg_service_folder_list = 'tests\\TEST_CONFIG_FOLDER\\service-files'

    dynamite_config = DynamiteConfig(arg_config_path, arg_service_folder_list)

    path_list = dynamite_config.ServiceFiles.PathList

    assert len(path_list) == 2
    assert 'tests\\TEST_CONFIG_FOLDER\\service-files' in path_list
    assert absolute_path_of_service_folder in path_list

def test_correct_values_in_dynamiteConfig_object_after_creation(path_to_tmp_dynamite_config_file):
    arg_config_path = path_to_tmp_dynamite_config_file
    arg_service_folder_list = 'tests\\TEST_CONFIG_FOLDER\\service-files'

    dynamite_config = DynamiteConfig(arg_config_path, arg_service_folder_list)

    service_files = dynamite_config.ServiceFiles
    assert len(service_files.PathList) == 2
    assert 'tests\\TEST_CONFIG_FOLDER\\service-files' in service_files.PathList
    assert absolute_path_of_service_folder in service_files.PathList

    fleet_api_endpoint = dynamite_config.FleetAPIEndpoint
    assert fleet_api_endpoint.ip == "172.17.8.101"
    assert fleet_api_endpoint.port == 49153

    etcd = dynamite_config.ETCD
    assert etcd.application_base_path == '/services'

    service = dynamite_config.Service
    assert service.apache is not None
    assert service.haproxy is not None
    assert service.apache.type == 'webserver'
    assert 'zurmo_application' in service.apache.service_dependency
    assert 'zurmo_config' in service.apache.service_dependency
    assert service.haproxy.service_dependency is None
    assert service.haproxy.scale_up_policy is None

    scaling_policy = dynamite_config.ScalingPolicy
    assert scaling_policy.scale_up is not None
    assert scaling_policy.scale_down is not None
    assert scaling_policy.scale_up.metric == 'response_time'
    assert scaling_policy.scale_up.threshold == 250
    assert scaling_policy.scale_down.service_type == 'apache'
    assert scaling_policy.scale_down.cooldown_period_unit == 'minute'

# if __name__ == '__main__':
#     pass
#
#     print(type(dynamite_config_yaml))
#     print(type(x))
#     print(x['Dynamite'])
#     print(x['Dynamite']['FleetAPIEndpoint'])
#     print(x['Dynamite']['FleetAPIEndpoint']['IP'])