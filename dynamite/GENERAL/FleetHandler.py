__author__ = 'brnr'

import requests
import json

class FleetHandler(object):

    # Instance Variables
    ip = None
    port = None

    fleet_base_url = None
    fleet_machines_url = None
    fleet_units_url = None

    is_connected = None

    http_json_content_type_header = {'Content-Type': 'application/json'}

    def connect(self):
        pass

    def disconnect(self):
        pass

    def test_connection(self):
        request_url = self.fleet_machines_url

        response = requests.get(request_url)

        if response.status_code == 200:
            self.is_connected = True
            return True
        else:
            return False

    def submit(self, service_name, json_definition_str):
        request_url = self.fleet_units_url + service_name
        request_header = self.http_json_content_type_header
        request_data = json_definition_str
        #
        # print(request_url)
        # print(request_header)
        # print(request_data)
        print(type(request_data))

        # curl http://127.0.0.1:49153/fleet/v1/units/example.service -H "Content-Type: application/json" -X PUT -d @example.service.json
        # Successful Response-Code: 201
        response = requests.put(request_url, headers=request_header, data=request_data)

        # json_response = json.loads(response.text)
        # print(json_response)
        print(response.status_code)
        print(response.text)

    def destroy(self):
        pass

    def load(self):
        pass

    def unload(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def __init__(self, ip, port):

        # Maybe add some more validation checks for <ip> and <port> argument
        if ip is None or not isinstance(ip, str):
            raise ValueError("Error: <ip> argument needs to be of type <str> (e.g.: '127.0.0.1'")

        if port is None or not isinstance(port, str):
            raise ValueError("Error: <port> argument needs to be of type <str>")

        self.ip = ip
        self.port = port
        self.fleet_base_url = "http://" + self.ip + ":" + self.port + "/fleet/v1/"
        self.fleet_machines_url = self.fleet_base_url + "machines"
        self.fleet_units_url = self.fleet_base_url + "units/"

        if not self.test_connection():
            raise ConnectionError("Error: Could not establish connection to Fleet")


    def __str__(self):
        pass


if __name__ == '__main__':
    # json_response = json.loads(response.text)
    # print(json_response)
    # print(type(json_response))

    x = FleetHandler("127.0.0.1", "49153")