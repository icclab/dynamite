__author__ = 'brnr'

import requests
import json


class FleetServiceHandler(object):

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

    # Returns HTTP Response Status
    # Successful Response-Code: 201
    # Service Exists Already Response-Code: 204
    def submit(self, service_name, json_definition_str):
        request_url = self.fleet_units_url + service_name
        request_header = self.http_json_content_type_header
        request_data = json_definition_str

        # curl http://127.0.0.1:49153/fleet/v1/units/example.service -H "Content-Type: application/json" -X PUT -d @example.service.json
        response = requests.put(request_url, headers=request_header, data=request_data)

        return response.status_code

    # Returns HTTP Response Status
    # Successful Response-Code: 204
    # Service Does Not Exist: 404
    def destroy(self, service_name):
        request_url = self.fleet_units_url + service_name

        response = requests.delete(request_url)

        return response.status_code

    # load, unload, start and stop should all take advantage of the _change_state function
    def _change_state(self, state):
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

    x = FleetServiceHandler("127.0.0.1", "49153")