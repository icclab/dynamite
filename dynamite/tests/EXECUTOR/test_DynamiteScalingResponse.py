__author__ = 'bloe'

from dynamite.EXECUTOR.DynamiteScalingResponse import DynamiteScalingResponse
from dynamite.EXECUTOR.DynamiteScalingResponse import DynamiteScalingRequest
from dynamite.EXECUTOR.DynamiteScalingCommand import DynamiteScalingCommand
from unittest.mock import Mock

class TestDynamiteScalingResponse:

    test_json = """
        {
            "command": "scale_down",
            "service_name": "apache_service_name",
            "service_instance_name": "apache_service_instance_name",
            "failure_counter": 4,
            "success": true
        }
    """

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
        scaling_response = DynamiteScalingResponse.from_json_string(self.test_json)
        assert scaling_response.command == DynamiteScalingCommand.SCALE_DOWN
        assert scaling_response.service_instance_name == "apache_service_instance_name"
        assert scaling_response.service_name == "apache_service_name"
        assert scaling_response.failure_counter == 4
        assert scaling_response.success is True

    def test_to_json_string(self):
        scaling_response = DynamiteScalingResponse()
        scaling_response.command = DynamiteScalingCommand.SCALE_DOWN
        scaling_response.failure_counter = 4
        scaling_response.service_instance_name = "apache_service_instance_name"
        scaling_response.service_name = "apache_service_name"
        scaling_response.success = False
        scaling_response.message_processed_callback = lambda: None

        result_json = scaling_response.to_json_string()
        result_response = DynamiteScalingResponse.from_json_string(result_json, scaling_response.message_processed_callback)
        assert result_response == scaling_response


    def test_message_processed_with_callback(self):

        callback = Mock()
        scaling_response = DynamiteScalingResponse.from_json_string(self.test_json, message_processed_callback=callback)
        scaling_response.message_processed()
        callback.assert_called_once_with()

    def test_message_processed_without_callback(self):

        scaling_response = DynamiteScalingResponse.from_json_string(self.test_json)
        scaling_response.message_processed()
