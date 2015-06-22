__author__ = 'bloe'

from dynamite.EXECUTOR.DynamiteScalingRequest import DynamiteScalingRequest
from dynamite.ENGINE.ScalingAction import ScalingAction, DynamiteScalingCommand
from dynamite.EXECUTOR.DynamiteScalingCommand import DynamiteScalingCommand

class TestDynamiteScalingRequest:

    def test_init_from_json_string(self):
        json_string = """
            {
                "service_instance_name": "apache_service_instance",
                "service_name": "apache_service",
                "command": "scale_up",
                "failure_counter": 8
            }
            """
        request = DynamiteScalingRequest.from_json_string(json_string)
        assert request.command == DynamiteScalingCommand.SCALE_UP
        assert request.service_name == "apache_service"
        assert request.service_instance_name == "apache_service_instance"
        assert request.failure_counter == 8

    def test_init_from_scaling_action(self):
        action = ScalingAction("apache_service")
        action.command = DynamiteScalingCommand.SCALE_UP
        action.service_instance_name = "apache_instance_name"
        action.uuid = "apache_uuid"

        request = DynamiteScalingRequest.from_scaling_action(action)
        assert request.service_name == action.service_name
        assert request.service_instance_name == action.service_instance_name
        assert request.command == action.command
        assert request.failure_counter == 0

    def test_to_json_string(self):
        scaling_request = DynamiteScalingRequest()
        scaling_request.failure_counter = 7
        scaling_request.service_instance_name = "apache_service_instance_name"
        scaling_request.service_name = "apache_service_name"
        scaling_request.command = DynamiteScalingCommand.SCALE_DOWN

        json = scaling_request.to_json_string()
        copy = DynamiteScalingRequest.from_json_string(json)

        assert copy == scaling_request
