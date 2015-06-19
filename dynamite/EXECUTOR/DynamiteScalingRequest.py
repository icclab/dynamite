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

    def __init__(self, scaling_request_string):
        if isinstance(scaling_request_string, str):
            self.scaling_request_string = scaling_request_string
        else:
            raise IllegalArgumentError("Error: argument <scaling_request_string> needs to be of type <str>")

        scaling_request_json = json.loads(self.scaling_request_string)

        self.command = scaling_request_json["command"]
        self.service_name = scaling_request_json["service_name"]
        self.service_instance_name = scaling_request_json["service_instance_name"]
        self.failure_counter = scaling_request_json["failure_counter"]