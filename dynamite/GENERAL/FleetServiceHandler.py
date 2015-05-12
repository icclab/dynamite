__author__ = 'brnr'

import requests
import json

from dynamite.GENERAL.FleetService import FleetService, FLEET_STATE_STRUCT
from dynamite.GENERAL.DynamiteExceptions import IllegalArgumentError


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
    def submit(self, fleet_service):
        if not isinstance(fleet_service, FleetService):
            raise IllegalArgumentError("Error: Argument <fleet_service> not instance of type <dynamite.GENERAL.FleetService>")

        if fleet_service.state is None:
            service_name = fleet_service.service_config_details.name_of_unit_file

            fleet_service.unit_file_details_json_dict["desiredState"] = FLEET_STATE_STRUCT.INACTIVE
            fleet_service.state = FLEET_STATE_STRUCT.INACTIVE

            service_json = json.dumps(fleet_service.unit_file_details_json_dict)

            request_url = self.fleet_units_url + service_name
            request_header = self.http_json_content_type_header
            request_data = service_json

            # curl http://127.0.0.1:49153/fleet/v1/units/example.service -H "Content-Type: application/json" -X PUT -d @example.service.json
            response = requests.put(request_url, headers=request_header, data=request_data)

            return response.status_code
        else:
            return None


    # Returns HTTP Response Status
    # Successful Response-Code: 204
    # Service Does Not Exist: 404
    def destroy(self, fleet_service):
        if fleet_service.state is not None:

            fleet_service.unit_file_details_json_dict["desiredState"] = None
            fleet_service.state = None

            service_name = fleet_service.service_config_details.name_of_unit_file
            request_url = self.fleet_units_url + service_name

            response = requests.delete(request_url)

            return response.status_code
        else:
            return None

    # load, unload, start and stop should all take advantage of the _change_state function
    def _change_state(self, fleet_service, new_state):

        if new_state not in FLEET_STATE_STRUCT.ALLOWED_STATES:
            raise IllegalArgumentError("Error: <new_state> values not allowed. Only allowed values are: " + FLEET_STATE_STRUCT.ALLOWED_STATES)

        fleet_service.state = new_state
        fleet_service.unit_file_details_json_dict["desiredState"] = new_state

        service_name = fleet_service.service_config_details.name_of_unit_file

        request_url = self.fleet_units_url + service_name
        request_header = self.http_json_content_type_header
        request_data = json.dumps({"desiredState": new_state})

        # curl http://127.0.0.1:49153/fleet/v1/units/example.service -H "Content-Type: application/json" -X PUT -d '{"desiredState": "loaded"}'
        response = requests.put(request_url, headers=request_header, data=request_data)

        return response.status_code

    def load(self, fleet_service):
        if not isinstance(fleet_service, FleetService):
            raise IllegalArgumentError("Error: Argument <fleet_service> not instance of type <dynamite.GENERAL.FleetService>")

        if fleet_service.state == FLEET_STATE_STRUCT.INACTIVE:
            response = self._change_state(fleet_service, FLEET_STATE_STRUCT.LOADED)
            return response
        elif fleet_service.state is None:
            self.submit(fleet_service)
            response = self._change_state(fleet_service, FLEET_STATE_STRUCT.LOADED)
            return response
        else:
            return None

    def unload(self, fleet_service):
        if not isinstance(fleet_service, FleetService):
            raise IllegalArgumentError("Error: Argument <fleet_service> not instance of type <dynamite.GENERAL.FleetService>")

        if fleet_service.state == FLEET_STATE_STRUCT.LOADED or fleet_service.state == FLEET_STATE_STRUCT.LAUNCHED:
            response = self._change_state(fleet_service, FLEET_STATE_STRUCT.INACTIVE)
            return response
        else:
            return None

    def start(self, fleet_service):
        if not isinstance(fleet_service, FleetService):
            raise IllegalArgumentError("Error: Argument <fleet_service> not instance of type <dynamite.GENERAL.FleetService>")

        if fleet_service.state == FLEET_STATE_STRUCT.INACTIVE or fleet_service.state == FLEET_STATE_STRUCT.LOADED:
            response = self._change_state(fleet_service, FLEET_STATE_STRUCT.LAUNCHED)
            return response
        elif fleet_service.state is None:
            self.submit(fleet_service)
            response = self._change_state(fleet_service, FLEET_STATE_STRUCT.LAUNCHED)
            return response
        else:
            return None

    def stop(self, fleet_service):
        if not isinstance(fleet_service, FleetService):
            raise IllegalArgumentError("Error: Argument <fleet_service> not instance of type <dynamite.GENERAL.FleetService>")

        if fleet_service.state == FLEET_STATE_STRUCT.LAUNCHED:
            response = self._change_state(fleet_service, FLEET_STATE_STRUCT.LOADED)
            return response
        else:
            return None


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