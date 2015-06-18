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

    def to_json_string(self):
        instance_dict = {}

        for variable, value in self.__dict__.items():
            instance_dict[variable] = value

        json_string = json.dumps(instance_dict)

        return json_string

    def __init__(self, dynamite_scaling_request, success):

        if not isinstance(success, bool):
            raise IllegalArgumentError("Error: argument <success> needs to be of type <bool>")

        if isinstance(dynamite_scaling_request, DynamiteScalingRequest) and dynamite_scaling_request is not None:
            self.success = success
            self.command = dynamite_scaling_request.command
            self.service_name = dynamite_scaling_request.service_name
            self.service_instance_name = dynamite_scaling_request.service_instance_name
            self.failure_counter = dynamite_scaling_request.failure_counter

        else:
            raise IllegalArgumentError("Error: argument <scaling_request_string> needs to be of type <str>")