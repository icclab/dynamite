__author__ = 'brnr'

import json
from dynamite.GENERAL.DynamiteExceptions import IllegalArgumentError

class DynamiteScalingRequest(object):
    scaling_request_string = None

    command = None
    service_name = None
    service_instance_name = None
    failure_counter = None

    def to_json_string(self):
        instance_dict = {}

        for variable, value in self.__dict__.items():
            instance_dict[variable] = value

        json_string = json.dumps(instance_dict)

        return json_string

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @classmethod
    def from_scaling_action(cls, scaling_action):
        request = DynamiteScalingRequest()
        request.service_name = scaling_action.service_name
        request.service_instance_name = scaling_action.service_instance_name
        request.command = scaling_action.command
        request.failure_counter = 0
        return request

    @classmethod
    def from_json_string(cls, scaling_request_string):
        if not isinstance(scaling_request_string, str):
            raise IllegalArgumentError("Error: argument <scaling_request_string> needs to be of type <str>")

        scaling_request_json = json.loads(scaling_request_string)
        scaling_request = DynamiteScalingRequest()

        scaling_request.command = scaling_request_json["command"]
        scaling_request.service_name = scaling_request_json["service_name"]
        scaling_request.service_instance_name = scaling_request_json["service_instance_name"]
        scaling_request.failure_counter = scaling_request_json["failure_counter"]
        return scaling_request
