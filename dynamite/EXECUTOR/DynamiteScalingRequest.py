__author__ = 'brnr'

import json
from dynamite.GENERAL.DynamiteExceptions import IllegalArgumentError

class DynamiteScalingRequest(object):

    command = None
    service_name = None
    service_instance_name = None
    failure_counter = None
    message_processed_callback = None

    def __repr__(self):
        return "DynamiteScalingRequest(" \
               "command=\"{}\", " \
               "service_name=\"{}\", " \
               "service_instance_counter=\"{}\", " \
               "failure_counter=\"{}\", " \
               .format(
                    self.command,
                    self.service_name,
                    self.service_instance_name,
                    self.failure_counter,
               )

    def to_json_string(self):
        instance_dict = {}

        for variable, value in self.__dict__.items():
            instance_dict[variable] = value

        json_string = json.dumps(instance_dict)

        return json_string

    def message_processed(self):
        if self.message_processed_callback is not None:
            self.message_processed_callback()

    def __eq__(self, other):
        if other is None:
            return False
        return self.command == other.command \
            and self.failure_counter == other.failure_counter \
            and self.service_instance_name == other.service_instance_name \
            and self.service_name == other.service_name

    def __repr__(self):
        return "DynamiteScalingRequest(service_name={},service_instance_name={},failure_counter={},command={})".format(
            self.service_name,
            self.service_instance_name,
            repr(self.failure_counter),
            repr(self.command)
        )

    @classmethod
    def from_service(cls, service, command, service_instance_name=None):
        request = DynamiteScalingRequest()
        request.service_name = service.name
        request.service_instance_name = service_instance_name
        request.failure_counter = 0
        request.command = command
        return request

    @classmethod
    def from_scaling_action(cls, scaling_action):
        request = DynamiteScalingRequest()
        request.service_name = scaling_action.service_name
        request.service_instance_name = scaling_action.service_instance_name
        request.command = scaling_action.command
        request.failure_counter = 0
        return request

    @classmethod
    def from_json_string(cls, scaling_request_string, message_processed_callback=None):
        if not isinstance(scaling_request_string, str):
            raise IllegalArgumentError("Error: argument <scaling_request_string> needs to be of type <str>")

        scaling_request_json = json.loads(scaling_request_string)
        scaling_request = DynamiteScalingRequest()
        scaling_request.message_processed_callback = message_processed_callback
        scaling_request.command = scaling_request_json["command"]
        scaling_request.service_name = scaling_request_json["service_name"]
        scaling_request.service_instance_name = scaling_request_json["service_instance_name"]
        scaling_request.failure_counter = scaling_request_json["failure_counter"]
        return scaling_request
