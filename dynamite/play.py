__author__ = 'brnr'

import argparse
import os
import platform
import yaml

import requests

from dynamite.INIT.DynamiteConfig import DynamiteConfig
from dynamite.INIT.DynamiteServiceHandler import DynamiteServiceHandler

if __name__ == '__main__':

    # cwd = os.path.abspath(os.path.dirname(__file__))
    # print(cwd)

    path_to_config_file = "tests\\TEST_CONFIG_FOLDER\\config.yaml"
    service_folder_list = ['C:\\Users\\brnr\\PycharmProjects\\dynamite\\dynamite\\tests\\TEST_CONFIG_FOLDER\\service-files']

    dynamite_config = DynamiteConfig(path_to_config_file, service_folder_list)
    service_handler = DynamiteServiceHandler(dynamite_config)

    example_service_json = service_handler.ServiceJSONObjectDict['example.service']

    # curl http://127.0.0.1:49153/fleet/v1/units/example.service -H "Content-Type: application/json" -X PUT -d @example.service.json

    headers = {'Content-Type': 'application/json'}
    service_name = 'example.service'

    # Successful Response-Code: 201
    r = requests.put("http://127.0.0.1:49153/fleet/v1/units/" + service_name, headers=headers, data=example_service_json)

    #print(r.headers)
    #print(r.status_code)
    # with open('tests\\TEST_CONFIG_FOLDER\\json-files\\example.service.json', 'w') as outfile:
    #     outfile.write(example_service_json)