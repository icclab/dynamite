__author__ = 'bloe'

import time
from multiprocessing import Value
from dynamite import Dynamite
from dynamite.EXECUTOR.DynamiteScalingRequest import DynamiteScalingRequest
from dynamite.EXECUTOR.DynamiteScalingCommand import DynamiteScalingCommand

class TestExecutor(Dynamite.Dynamite):

    _scaling_response_receiver = None
    _scaling_action_sender = None

    def __init__(self):
        super(TestExecutor, self).__init__()
        self._exit_flag = Value('i', 0)
        self._scaling_response_receiver = None
        self._scaling_action_sender = None

    def run(self):

        self.init_env()
        self.init_arguments()
        config = self.parse_config()
        self.create_communication_queues()

        self._scaling_response_receiver = self._message_sender_receiver_factory.create_response_receiver()
        self._scaling_action_sender = self._message_sender_receiver_factory.create_request_sender()

        # only start the executor after initializing dynamite
        try:
            self.start_executor()
            self._start_sending_scaling_requests()
        finally:
            self._exit_flag.value = 1

        self._dynamite_executor.join()

    def _start_sending_scaling_requests(self):
        self._create_a_service()
        time.sleep(20)
        self._destroy_a_service(12021)
        time.sleep(20)

        self._create_example_service()
        time.sleep(20)
        self._destroy_example_service()
        time.sleep(20)
        pass

    def _create_example_service(self):
        self._create_service("example", None)

    def _destroy_example_service(self):
        self._destroy_service("example", "example.service")

    def _create_a_service(self):
        self._create_service("a", None)

    def _destroy_a_service(self, instance_number):
        self._destroy_service("a", "a@" + str(instance_number) + ".service")

    def _destroy_service(self, service_name, service_instance_name, failure_counter=0):
        request = DynamiteScalingRequest()
        request.command = DynamiteScalingCommand.SCALE_DOWN
        request.service_name = service_name
        request.service_instance_name = service_instance_name
        request.failure_counter = failure_counter
        self._scaling_action_sender.send_action(request)

    def _create_service(self, service_name, service_instance_name, failure_counter=0):
        request = DynamiteScalingRequest()
        request.command = DynamiteScalingCommand.SCALE_UP
        request.service_name = service_name
        request.service_instance_name = service_instance_name
        request.failure_counter = failure_counter
        self._scaling_action_sender.send_action(request)

if __name__ == '__main__':
    dynamite = TestExecutor()
    dynamite.run()
