__author__ = 'brnr'

from dynamite.GENERAL.DynamiteExceptions import IllegalArgumentError
from dynamite.EXECUTOR.DynamiteScalingRequest import DynamiteScalingRequest
import json

class DynamiteScalingResponse(object):

    command = None
    service_name = None
    service_instance_name = None
    failure_counter = None
    success = None
    message_processed_callback = None

    UNSERIALIZABLE_VARIABLES = ["message_processed_callback"]

    def to_json_string(self):
        instance_dict = {}

        for variable, value in self.__dict__.items():
            if variable not in self.UNSERIALIZABLE_VARIABLES:
                instance_dict[variable] = value

        json_string = json.dumps(instance_dict)

        return json_string

    def __repr__(self):
        return "DynamiteScalingResponse(command={},service_name={},service_instance_name={},failure_counter={},success={})".\
            format(self.command, self.service_name, self.service_instance_name, self.failure_counter, self.success)

    def __eq__(self, other):
        if other is None:
            return False

        return self.service_name == other.service_name and \
            self.service_instance_name == other.service_instance_name and \
            self.command == other.command and \
            self.success == other.success and \
            self.failure_counter == other.failure_counter

    def message_processed(self):
        if self.message_processed_callback is not None:
            self.message_processed_callback()

    @staticmethod
    def from_scaling_request(scaling_request, success):
        if not isinstance(success, bool):
            raise IllegalArgumentError("Error: argument <success> needs to be of type <bool>")
        if not isinstance(scaling_request, DynamiteScalingRequest) or scaling_request is None:
            raise IllegalArgumentError("Error: argument <scaling_request_string> needs to be of type <str>")

        scaling_response = DynamiteScalingResponse()
        scaling_response.success = success
        scaling_response.command = scaling_request.command
        scaling_response.service_name = scaling_request.service_name
        scaling_response.service_instance_name = scaling_request.service_instance_name
        scaling_response.failure_counter = scaling_request.failure_counter
        return scaling_response

    @staticmethod
    def from_json_string(json_string, message_processed_callback=None):
        scaling_response_json = json.loads(json_string)
        scaling_response = DynamiteScalingResponse()
        scaling_response.message_processed_callback = message_processed_callback
        scaling_response.success = scaling_response_json["success"]
        scaling_response.command = scaling_response_json["command"]
        scaling_response.service_name = scaling_response_json["service_name"]
        scaling_response.service_instance_name = scaling_response_json["service_instance_name"]
        scaling_response.failure_counter = scaling_response_json["failure_counter"]
        return scaling_response
