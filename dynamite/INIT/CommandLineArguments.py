__author__ = 'bloe'

import logging

class CommandLineArguments:

    config_path = None
    service_folder = None
    etcd_endpoint = None
    fleet_endpoint = None
    rabbitmq_endpoint = None

    def __init__(self, argument_parser_result):
        self._logger = logging.getLogger(__name__)

        self.service_folder = argument_parser_result.service_folder
        self.etcd_endpoint = argument_parser_result.etcd_endpoint
        self.config_path = argument_parser_result.config_file
        self.rabbitmq_endpoint = argument_parser_result.rabbitmq_endpoint
        self.fleet_endpoint = argument_parser_result.fleet_endpoint

    def log_arguments(self):
        self._logger.info("Using ectd endpoint %s", self.etcd_endpoint)
        self._logger.info("Using config path %s", self.config_path)
        self._logger.info("Using fleet endpoint %s", self.fleet_endpoint)
        if self._rabbitmq_endpoint_argument:
            self._logger.info("Using rabbitmq endpoint %s", self.rabbitmq_endpoint)