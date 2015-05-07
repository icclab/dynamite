__author__ = 'brnr'

import yaml
import pytest
import os

from dynamite.INIT.DynamiteConfig import DynamiteConfig

# @pytest.fixture(scope="module")
# def path_list_to_service_files():
#     path_list = []
#     path_a =

@pytest.fixture(scope="module")
def path_to_tmp_dynamite_config_file(request):

    name_of_tmp_config_file = "tmp_test_dynamite_config.yaml"
    path_to_tmp_config_file = "tests/INIT"

    tmp_config_file = os.path.join(path_to_tmp_config_file, name_of_tmp_config_file)

    dynamite_yaml_test_config_dict = {'Dynamite': {
      'ServiceFiles': {
        'PathList': ['C:\\Users\\brnr\\PycharmProjects\\dynamite\\dynamite\\tests\\TEST_CONFIG_FOLDER\\service-files']
      },
      'FleetAPIEndpoint': {
        'ip': '172.17.8.101',
        'port': 49153
      },
      'ETCD': {
        'ip_api_endpoint': '127.0.0.1',
        'port_api_endpoint': 4001,
        'application_base_path': '/services'
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
          'service': 'haproxy',
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
          'service': 'apache',
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
    }}

    dynamite_config_yaml = yaml.dump(dynamite_yaml_test_config_dict)

    with open(tmp_config_file, "w") as tmp_yaml_config_file:
            tmp_yaml_config_file.write(dynamite_config_yaml)

    @request.addfinalizer
    def teardown():
        tmp_yaml_config_file.close()
        os.remove(tmp_config_file)


    cwd = os.path.abspath(os.path.dirname(__file__))
    path_to_tmp_config = os.path.join(cwd,name_of_tmp_config_file)

    return path_to_tmp_config


def test_create_dynamiteConfig_object_with_arg_config_path_argument(path_to_tmp_dynamite_config_file):
    arg_config_path = path_to_tmp_dynamite_config_file

    dynamite_config = DynamiteConfig(arg_config_path)
    assert dynamite_config

def test_create_dynamiteConfig_object_with_arg_config_path_and_arg_service_folder_list_argument(path_to_tmp_dynamite_config_file):
    arg_config_path = path_to_tmp_dynamite_config_file
    arg_service_folder_list = ['tests\\TEST_CONFIG_FOLDER\\service-files']

    dynamite_config = DynamiteConfig(arg_config_path, arg_service_folder_list)
    assert dynamite_config

    path_list = dynamite_config.ServiceFiles.PathList

    assert len(path_list) == 2
    assert 'tests\\TEST_CONFIG_FOLDER\\service-files' in path_list
    assert 'C:\\Users\\brnr\\PycharmProjects\\dynamite\\dynamite\\tests\\TEST_CONFIG_FOLDER\\service-files' in path_list


# if __name__ == '__main__':
#     pass
#
    # print(type(dynamite_config_yaml))
    # print(type(x))
    # print(x['Dynamite'])
    # print(x['Dynamite']['FleetAPIEndpoint'])
    # print(x['Dynamite']['FleetAPIEndpoint']['IP'])