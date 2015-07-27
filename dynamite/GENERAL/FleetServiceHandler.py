__author__ = 'brnr'

import requests
import json
import logging

from dynamite.GENERAL.FleetService import FleetService, FLEET_STATE_STRUCT
from dynamite.GENERAL.DynamiteExceptions import IllegalArgumentError
from dynamite.GENERAL.Retry import retry, retry_on_condition

class FleetSubmissionError(Exception):
    pass

class FleetCommunicationError(Exception):
    pass

class FleetStartError(Exception):
    pass

class FleetDestroyError(Exception):
    pass

class FleetServiceHandler(object):

    # Instance Variables
    ip = None
    port = None

    fleet_base_url = None
    fleet_machines_url = None
    fleet_units_url = None

    is_connected = None

    http_json_content_type_header = {'Content-Type': 'application/json'}

    def __init__(self, ip, port):

        self._logger = logging.getLogger(__name__)

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
    def submit(self, fleet_service, fleet_service_instance):
        if not isinstance(fleet_service_instance, FleetService.FleetServiceInstance):
            raise IllegalArgumentError("Error: Argument <fleet_service> not instance of type <dynamite.GENERAL.FleetService.FleetServiceInstance>")

        if fleet_service.has_attached_services():
            for attached_service in fleet_service.attached_services:
                for name, attached_service_instance in attached_service.fleet_service_instances.items():
                    self.submit(attached_service, attached_service_instance)

        if fleet_service_instance.state is None:
            service_name = fleet_service_instance.name

            # fleet_service_instance.unit_file_details_json_dict["desiredState"] = FLEET_STATE_STRUCT.INACTIVE
            fleet_service.unit_file_details_json_dict["desiredState"] = FLEET_STATE_STRUCT.INACTIVE
            fleet_service_instance.state = FLEET_STATE_STRUCT.INACTIVE

            #service_json = json.dumps(fleet_service_instance.unit_file_details_json_dict)
            service_json = json.dumps(fleet_service.unit_file_details_json_dict)

            request_url = self.fleet_units_url + service_name
            request_header = self.http_json_content_type_header
            request_data = service_json

            # curl http://127.0.0.1:49153/fleet/v1/units/example.service -H "Content-Type: application/json" -X PUT -d @example.service.json
            response = requests.put(request_url, headers=request_header, data=request_data)

            self._check_if_unit_exists_and_retry_if_not(fleet_service_instance.name)
            return response.status_code
        else:
            return None

    @retry(FleetSubmissionError, tries=7, delay=1, backoff=1.5, logger=logging.getLogger(__name__))
    @retry(FleetCommunicationError, tries=7, delay=1, backoff=1.5, logger=logging.getLogger(__name__))
    def _check_if_unit_exists_and_retry_if_not(self, fleet_unit):
        request_url = self.fleet_units_url + fleet_unit
        response = requests.get(request_url)
        if response.status_code == requests.codes.not_found:
            raise FleetSubmissionError("Submitted unit is in an invalid state: {}".format(fleet_unit))
        else:
            try:
                response.raise_for_status()
            except requests.HTTPError as httpError:
                raise FleetCommunicationError(
                    "Could not talk to fleet to check if {} exists".format(fleet_unit)
                ) from httpError

    @retry(FleetCommunicationError, tries=7, delay=1, backoff=1.5, logger=logging.getLogger(__name__))
    def get_state_of_unit_and_retry_on_error(self, fleet_unit):
        request_url = self.fleet_units_url + fleet_unit
        response = requests.get(request_url)
        try:
            response.raise_for_status()
        except requests.HTTPError as httpError:
            raise FleetCommunicationError(
                "Unable to communicate with fleet while trying to get the state of: {}!".format(fleet_unit)
            ) from httpError
        json_dictionary_of_response = json.loads(response.content.decode('utf-8'))
        if "currentState" in json_dictionary_of_response:
            return json_dictionary_of_response["currentState"]
        else:
            return None

    # Returns HTTP Response Status
    # Successful Response-Code: 204
    # Service Does Not Exist: 404
    def destroy(self, fleet_service_instance):
        if fleet_service_instance.state is not None:

            # Destroy attached services if one should exist
            if fleet_service_instance.has_attached_services():
                for attached_service_instance in fleet_service_instance.attached_services:
                    self.destroy(attached_service_instance)

            # fleet_service_instance.unit_file_details_json_dict["desiredState"] = None
            fleet_service_instance.state = None

            service_name = fleet_service_instance.name
            request_url = self.fleet_units_url + service_name

            response = requests.delete(request_url)
            # if service does not exist destroy has no effect, but do not treat it as error
            if response.status_code != 404:
                try:
                    response.raise_for_status()
                    self._check_if_service_destroyed_and_retry_if_not(service_name)
                except requests.HTTPError as httpError:
                    raise FleetCommunicationError(
                        "Unable to communicate with fleet while destroying {}!".format(service_name)
                    ) from httpError

            return response.status_code
        else:
            return None

    @retry_on_condition(tries=7, delay=1, backoff=1.5, logger=logging.getLogger(__name__), condition_fail_description="Service not yet destroyed")
    @retry(FleetCommunicationError, tries=7, delay=1, backoff=1.5, logger=logging.getLogger(__name__))
    def _check_if_service_destroyed_and_retry_if_not(self, service_instance_name):
        request_url = self.fleet_units_url + service_instance_name
        response = requests.get(request_url)
        service_is_still_found_in_fleet = response.status_code != 404
        if service_is_still_found_in_fleet:
            try:
                response.raise_for_status()
                return False
            except requests.HTTPError as httpError:
                raise FleetCommunicationError from httpError
        else:
            return True

    # load, unload, start and stop should all take advantage of the _change_state function
    @retry(FleetCommunicationError, tries=7, delay=1, backoff=1.5, logger=logging.getLogger(__name__))
    def _change_state(self, fleet_service_instance, new_state):

        if new_state not in FLEET_STATE_STRUCT.ALLOWED_STATES:
            raise IllegalArgumentError("Error: <new_state> values not allowed. Only allowed values are: " + FLEET_STATE_STRUCT.ALLOWED_STATES)

        fleet_service_instance.state = new_state
        #fleet_service.unit_file_details_json_dict["desiredState"] = new_state

        service_name = fleet_service_instance.name

        request_url = self.fleet_units_url + service_name
        request_header = self.http_json_content_type_header
        request_data = json.dumps({"desiredState": new_state})

        # curl http://127.0.0.1:49153/fleet/v1/units/example.service -H "Content-Type: application/json" -X PUT -d '{"desiredState": "loaded"}'
        response = requests.put(request_url, headers=request_header, data=request_data)

        try:
            response.raise_for_status()
        except requests.HTTPError as httpError:
            raise FleetCommunicationError(
                "Unable to communicate with fleet while changing the state of unit {} to {}!".format(
                    service_name,
                    new_state
                )
            ) from httpError

        return response.status_code

    def load(self, fleet_service, fleet_service_instance):
        if not isinstance(fleet_service_instance, FleetService.FleetServiceInstance):
            raise IllegalArgumentError("Error: Argument <fleet_service> not instance of type <dynamite.GENERAL.FleetService.FleetServiceInstance>")

        if fleet_service_instance.state == FLEET_STATE_STRUCT.INACTIVE:
            response = self._change_state(fleet_service_instance, FLEET_STATE_STRUCT.LOADED)

            # Also load attached services after parent service was loaded
            if fleet_service_instance.has_attached_services():
                for attached_service_instance in fleet_service_instance.attached_services:
                    response = self._change_state(attached_service_instance, FLEET_STATE_STRUCT.LOADED)

            return response
        elif fleet_service_instance.state is None:
            self.submit(fleet_service, fleet_service_instance)

            # Also load attached services after parent service was loaded
            if fleet_service_instance.has_attached_services():
                for attached_service_instance in fleet_service_instance.attached_services:
                    response = self._change_state(attached_service_instance, FLEET_STATE_STRUCT.LOADED)

            response = self._change_state(fleet_service_instance, FLEET_STATE_STRUCT.LOADED)
            return response
        else:
            return None

    def unload(self, fleet_service_instance):
        if not isinstance(fleet_service_instance, FleetService.FleetServiceInstance):
            raise IllegalArgumentError("Error: Argument <fleet_service> not instance of type <dynamite.GENERAL.FleetService.FleetServiceInstance>")

        if fleet_service_instance.state == FLEET_STATE_STRUCT.LOADED or fleet_service_instance.state == FLEET_STATE_STRUCT.LAUNCHED:
            self._change_state(fleet_service_instance, FLEET_STATE_STRUCT.INACTIVE)

        # Also unload attached services after parent service was unloaded
        if fleet_service_instance.has_attached_services():
            for attached_service_instances in fleet_service_instance.attached_services:
                self._change_state(attached_service_instances, FLEET_STATE_STRUCT.INACTIVE)

    def start(self, fleet_service, fleet_service_instance):
        if not isinstance(fleet_service_instance, FleetService.FleetServiceInstance):
            raise IllegalArgumentError("Error: Argument <fleet_service> not instance of type <dynamite.GENERAL.FleetService.FleetServiceInstance>")

        if fleet_service_instance.state == FLEET_STATE_STRUCT.INACTIVE or fleet_service_instance.state == FLEET_STATE_STRUCT.LOADED:
            response = self._change_state(fleet_service_instance, FLEET_STATE_STRUCT.LAUNCHED)

            # Also start service announcer after parent service was started
            if fleet_service_instance.has_attached_services():
                for attached_service in fleet_service_instance.attached_services:
                    response = self._change_state(attached_service, FLEET_STATE_STRUCT.LAUNCHED)

            return response
        elif fleet_service_instance.state is None:
            self.submit(fleet_service, fleet_service_instance)
            response = self._change_state(fleet_service_instance, FLEET_STATE_STRUCT.LAUNCHED)

            # Also start attached services after parent service was started
            if fleet_service_instance.has_attached_services():
                for attached_service_instance in fleet_service_instance.attached_services:
                    response = self._change_state(attached_service_instance, FLEET_STATE_STRUCT.LAUNCHED)

            services_started = self._check_if_service_and_attached_services_started(fleet_service_instance)
            if not services_started:
                raise FleetStartError(
                    "Could not start Service {} and or attached services!".format(
                        fleet_service_instance.name
                    )
                )

            return response
        else:
            return None

    @retry_on_condition(tries=7, delay=1, backoff=1.5, logger=logging.getLogger(__name__),
                        condition_fail_description="Service not in LAUNCHED state")
    def _check_if_service_and_attached_services_started(self, service_instance):
        state = self.get_state_of_unit_and_retry_on_error(service_instance.name)
        if state != FLEET_STATE_STRUCT.LAUNCHED:
            return False
        if service_instance.has_attached_services():
                for attached_service_instance in service_instance.attached_services:
                    state = self.get_state_of_unit_and_retry_on_error(attached_service_instance.name)
                    if state != FLEET_STATE_STRUCT.LAUNCHED:
                        return False
        return True

    def stop(self, fleet_service_instance):
        if not isinstance(fleet_service_instance, FleetService.FleetServiceInstance):
            raise IllegalArgumentError("Error: Argument <fleet_service> not instance of type <dynamite.GENERAL.FleetService.FleetServiceInstance>")

        if fleet_service_instance.state == FLEET_STATE_STRUCT.LAUNCHED:
            response = self._change_state(fleet_service_instance, FLEET_STATE_STRUCT.LOADED)

            # Also stop service announcer after parent service was stopped
            if fleet_service_instance.has_attached_services():
                for attached_service_instance in fleet_service_instance.attached_services:
                    response = self._change_state(attached_service_instance, FLEET_STATE_STRUCT.LOADED)

            return response
        else:
            return None

    # This function expects the parent service / the service definition
    # fleet_service is of type FleetService
    def create_new_fleet_service_instance(self, fleet_service, port_numbers=None, is_attached_service=False):

        if fleet_service is None or not isinstance(fleet_service, FleetService):
            raise ValueError("Error: <fleet_service> argument needs to be of type <dynamite.GENERAL.FleetService>")

        # Maybe this has to be clarified more clearly. Instance Name = Port Number
        instance_name = port_numbers if port_numbers is not None else fleet_service.get_next_port_numbers()

        if instance_name is None:
            return self._create_service_instance_without_template(fleet_service)
        else:
            return self._create_service_instance_from_template(fleet_service, instance_name)

    def _create_service_instance_without_template(self, fleet_service):
        # create instance with no instance name
        # make sure to only create one instance of this!
        # new_fleet_instance = FleetService(
        if len(fleet_service.fleet_service_instances) == 1:
            return None

        new_fleet_service_name = fleet_service.service_config_details.name_of_unit_file
        attached_service_instances = []

        if fleet_service.has_attached_services():
            for attached_service in fleet_service.attached_services:
                attached_service_instance = self.create_new_fleet_service_instance(attached_service,
                                                                                   is_attached_service=True)
                attached_service_instances.append(attached_service_instance)

        new_fleet_instance = FleetService.FleetServiceInstance(new_fleet_service_name,
                                                               state=None,
                                                               attached_services=attached_service_instances)

        fleet_service.fleet_service_instances[new_fleet_service_name] = new_fleet_instance
        return new_fleet_instance

    def _create_service_instance_from_template(self, fleet_service, instance_name):
        # Don't create a new instance if there is already a maximum amount of services
        if len(fleet_service.fleet_service_instances) == fleet_service.service_config_details.max_instance:
            return None

        new_fleet_service_name = fleet_service.name + "@" + str(instance_name[0]) + ".service"

        attached_service_instances = []
        if fleet_service.has_attached_services():
            for attached_service in fleet_service.attached_services:
                attached_service_instance = self.create_new_fleet_service_instance(attached_service,
                                                                                   instance_name,
                                                                                   is_attached_service=True)
                attached_service_instances.append(attached_service_instance)

        new_fleet_instance = FleetService.FleetServiceInstance(new_fleet_service_name,
                                                               state=None,
                                                               attached_services=attached_service_instances)

        fleet_service.fleet_service_instances[new_fleet_service_name] = new_fleet_instance
        return new_fleet_instance

    # fleet_service expected type: dynamite.GENERAL.FleetService
    def remove_fleet_service_instance(self, fleet_service, fleet_service_instance_name=None, destroy_service=True):

        if fleet_service_instance_name is not None:
            instance_name = fleet_service_instance_name

        # Remove used port/instance numbers
        if fleet_service.used_port_numbers is not None:
            # e.g a@12021.service --> instance_number = 12021

            if fleet_service_instance_name is not None:
                instance_number = instance_name.split("@")
                instance_number = instance_number[1].split(".")
                instance_number = int(instance_number[0])

            else:
                try:
                    instance_number_index = fleet_service.used_port_numbers.index(0)
                    instance_number = fleet_service.used_port_numbers[instance_number_index - 1]
                    instance_name = fleet_service.name + "@" + str(instance_number) + ".service"
                except ValueError:
                    instance_number = fleet_service.used_port_numbers[-1]
                    instance_name = fleet_service.name + "@" + str(instance_number) + ".service"

        fleet_service_instance = fleet_service.fleet_service_instances[instance_name]

        if destroy_service:
            self.destroy(fleet_service_instance)
            service_destroyed = self._check_if_service_destroyed_and_retry_if_not(instance_name)
            if not service_destroyed:
                raise FleetDestroyError("Could not destroy unit {}".format(instance_name))

        if fleet_service.is_template:
            for i in range(fleet_service.service_config_details.ports_per_instance):
                fleet_service.used_port_numbers[fleet_service.used_port_numbers.index(instance_number+i)] = 0

        del fleet_service.fleet_service_instances[instance_name]

        return instance_name

    def __str__(self):
        pass


if __name__ == '__main__':
    # json_response = json.loads(response.text)
    # print(json_response)
    # print(type(json_response))

    x = FleetServiceHandler("127.0.0.1", "49153")
