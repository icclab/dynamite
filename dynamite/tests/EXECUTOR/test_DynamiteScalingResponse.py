__author__ = 'bloe'

from dynamite.EXECUTOR.DynamiteScalingResponse import DynamiteScalingResponse
from dynamite.EXECUTOR.DynamiteScalingResponse import DynamiteScalingRequest
from dynamite.EXECUTOR.DynamiteScalingCommand import DynamiteScalingCommand

class TestDynamiteScalingResponse:

    def test_from_scaling_request(self):
        scaling_request = DynamiteScalingRequest()
        scaling_request.command = DynamiteScalingCommand.SCALE_DOWN
        scaling_request.failure_counter = 4
        scaling_request.service_instance_name = "apache_service_instance_name"
        scaling_request.service_name = "apache_service_name"

        scaling_response = DynamiteScalingResponse.from_scaling_request(scaling_request, True)
        assert scaling_response.command == scaling_request.command
        assert scaling_response.service_instance_name == scaling_request.service_instance_name
        assert scaling_response.service_name == scaling_request.service_name
        assert scaling_response.failure_counter == scaling_request.failure_counter
        assert scaling_response.success is True

    def test_from_json_string(self):
        json = """
            {
                "command": "scale_down",
                "service_name": "apache_service_name",
                "service_instance_name": "apache_service_instance_name",
                "failure_counter": 4,
                "success": true
            }
        """
        scaling_response = DynamiteScalingResponse.from_json_string(json)
        assert scaling_response.command == DynamiteScalingCommand.SCALE_DOWN
        assert scaling_response.service_instance_name == "apache_service_instance_name"
        assert scaling_response.service_name == "apache_service_name"
        assert scaling_response.failure_counter == 4
        assert scaling_response.success is True
