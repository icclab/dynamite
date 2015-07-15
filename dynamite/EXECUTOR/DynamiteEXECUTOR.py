__author__ = 'brnr'

from multiprocessing import Process
from dynamite.INIT.DynamiteServiceHandler import DynamiteServiceHandler
from dynamite.INIT.DynamiteConfig import DynamiteConfig

from dynamite.EXECUTOR.DynamiteScalingResponse import DynamiteScalingResponse
from dynamite.EXECUTOR.DynamiteScalingCommand import DynamiteScalingCommand

import logging
import atexit
import time

# DynamiteExecutor is a Process which reads scaling request from a rabbitmq queue and creates or deletes fleet-services
# in a CoreOS Cluster

class DynamiteEXECUTOR(Process):

    EXECUTOR_POLL_DELAY_IN_SECONDS = 1

    _logger = None
    _exit_flag = None

    _etcd_endpoint = "127.0.0.1:4001"

    _scaling_request_receiver = None
    _scaling_response_sender = None

    _dynamite_service_handler = None
    _dynamite_config = None

    def __init__(self,
                 scaling_request_receiver,
                 scaling_response_sender,
                 exit_flag,
                 etcd_endpoint=None
                 ):
        super(DynamiteEXECUTOR, self).__init__()

        self._exit_flag = exit_flag
        self._etcd_endpoint = etcd_endpoint

        self._scaling_request_receiver = scaling_request_receiver
        self._scaling_response_sender = scaling_response_sender

        atexit.register(self._close_connections)

    def run(self):
        try:
            self._logger = logging.getLogger(__name__)
            self._logger.info("Initialized DynamiteEXECUTOR with configuration %s", str(self))

            self._create_dynamite_config(self._etcd_endpoint)
            self._create_dynamite_service_handler(self._dynamite_config, self._etcd_endpoint)

            self._scaling_request_receiver.connect()
            self._scaling_response_sender.connect()

            while self._exit_flag.value == 0:
                try:
                    scaling_request = self._scaling_request_receiver.receive()
                    if scaling_request is None:
                        time.sleep(self.EXECUTOR_POLL_DELAY_IN_SECONDS)
                        continue

                    self._process_received_request(scaling_request)
                except:
                    self._logger.exception("Unexpected exception in Executor component")
        finally:
            self._exit_flag.value = 1

    def _process_received_request(self, scaling_request):
        response = None
        if scaling_request.command == DynamiteScalingCommand.SCALE_UP:
            service_name = scaling_request.service_name
            response = self._dynamite_service_handler.add_new_fleet_service_instance(service_name)
        elif scaling_request.command == DynamiteScalingCommand.SCALE_DOWN:
            service_name = scaling_request.service_name
            service_instance_name = scaling_request.service_instance_name
            response = self._dynamite_service_handler.remove_fleet_service_instance(service_name, service_instance_name)

        scaling_success = True if response is not None else False
        scaling_response = DynamiteScalingResponse.from_scaling_request(scaling_request, scaling_success)
        self._scaling_response_sender.send_response(scaling_response)
        scaling_response.message_processed()

    def _create_dynamite_config(self, etcd_endpoint):
        self._dynamite_config = DynamiteConfig(etcd_endpoint=etcd_endpoint)

    def _create_dynamite_service_handler(self, dynamite_config, etcd_endpoint):
        self._dynamite_service_handler = DynamiteServiceHandler(dynamite_config=dynamite_config,
                                                               etcd_endpoint=etcd_endpoint)

    def __repr__(self):
        return "DynamiteEXECUTOR(" \
               "etcd_endpoint=\"{}\", " \
               "scaling_request_receiver=\"{}\", " \
               "scaling_response_sender=\"{}\", " \
               .format(
                    self._etcd_endpoint,
                    self._scaling_request_receiver,
                    self._scaling_response_sender,
               )

    def _close_connections(self):
        self._scaling_request_receiver.close()
        self._scaling_response_sender.close()

#   Scaling Request
#   {
#       "command": "scale_up / scale_down",
#       "service": "service_name (e.g. zurmo_apache)",
#       "service_instance_name" : "service_instance_name (e.g. zurmo_apache@8080.service)"  --> will only be set when scaling down, otherwise set to 'None'
#       "failure_counter" : <int> --> starts at 0 and is increased when a failure occurs
#   }
#
#   Scaling Response:
#   {
#       "success": "true / false"
#       "command": "scale_up / scale_down",
#       "service": "service_name (e.g. zurmo_apache)",
#       "service_instance_name" : "service_instance_name (e.g. zurmo_apache@8080.service)"  --> will only be set when scaling down, otherwise set to 'None'
#       "failure_counter" : <int> --> starts at 0 and is increased when a failure occurs
#   }
