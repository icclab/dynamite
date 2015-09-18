__author__ = 'brnr'

from multiprocessing import Process
from dynamite.INIT.DynamiteServiceHandler import DynamiteServiceHandler
from dynamite.INIT.DynamiteConfig import DynamiteConfig
from dynamite.GENERAL.FleetServiceHandler import FleetCommunicationError, FleetStartError, FleetSubmissionError, FleetDestroyError

from dynamite.EXECUTOR.DynamiteScalingResponse import DynamiteScalingResponse
from dynamite.EXECUTOR.DynamiteScalingCommand import DynamiteScalingCommand
from dynamite.GENERAL.Retry import retry, retry_on_condition

import logging
import atexit
import time

# DynamiteExecutor is a Process which reads scaling request from a rabbitmq queue and creates or deletes fleet-services
# in a CoreOS Cluster

class DynamiteEXECUTOR(Process):

    EXECUTOR_POLL_DELAY_IN_SECONDS = 1
    RETRY_FAILED_REQUESTS_TIMES = 5

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
                    pass
        finally:
            self._exit_flag.value = 1
    
    @retry(FleetSubmissionError, tries=7, delay=1, backoff=1.5, logger=logging.getLogger(__name__))
    @retry(FleetStartError, tries=7, delay=1, backoff=1.5, logger=logging.getLogger(__name__))
    @retry(FleetDestroyError, tries=7, delay=1, backoff=1.5, logger=logging.getLogger(__name__))
    @retry(FleetCommunicationError, tries=7, delay=1, backoff=1.5, logger=logging.getLogger(__name__))
    @retry(FleetStartError, tries=7, delay=1, backoff=1.5, logger=logging.getLogger(__name__))
    def _process_received_request(self, scaling_request, fail_count=0):
        scaling_success = False
        created_service_instance = None

        try:
            if scaling_request.command == DynamiteScalingCommand.SCALE_UP:
                service_name = scaling_request.service_name
                created_service_instance = self._dynamite_service_handler.add_new_fleet_service_instance(service_name)
            elif scaling_request.command == DynamiteScalingCommand.SCALE_DOWN:
                service_name = scaling_request.service_name
                service_instance_name = scaling_request.service_instance_name
                self._dynamite_service_handler.remove_fleet_service_instance(service_name, service_instance_name)
            scaling_success = True
        except FleetSubmissionError as fse:
            self._logger.exception("Submitting fleet file failed!")
            raise FleetSubmissionError from fse
        except FleetStartError:
            self._logger.exception("Starting fleet service failed!")
            if created_service_instance is not None:
                self._unload_unit(created_service_instance)
            raise FleetStartError from fse
        except FleetDestroyError as fde:
            self._logger.exception("Destroying fleet service failed!")
            raise FleetDestroyError from fde
        except FleetCommunicationError as fce:
            self._logger.exception("Communication with fleet failed!")
            raise FleetCommunicationError from fce

        scaling_response = DynamiteScalingResponse.from_scaling_request(scaling_request, scaling_success)
        self._scaling_response_sender.send_response(scaling_response)
        scaling_response.message_processed()

    def _unload_unit(self, created_service_instance):
        try:
            self._dynamite_service_handler.FleetServiceHandler.unload(created_service_instance)
        except FleetCommunicationError:
            self._logger.exception("Could not unload fleet file! {}".format(repr(created_service_instance)))

    def _retry_processing_request(self, scaling_request, fail_count):
        if fail_count < self.RETRY_FAILED_REQUESTS_TIMES:
            self._logger.error("Retrying processing request again!")
            self._process_received_request(scaling_request, fail_count=fail_count+1)
            return True
        else:
            self._logger.error("Retried {} times, giving up!".format(self.RETRY_FAILED_REQUESTS_TIMES))
            return False

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
