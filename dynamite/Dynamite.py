#!/usr/bin/env python3

__author__ = 'brnr'

import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

import argparse
import platform
import logging
from multiprocessing import Queue, Value

from dynamite.INIT.DynamiteINIT import DynamiteINIT
from dynamite.INIT.CommandLineArguments import CommandLineArguments
from dynamite.GENERAL.MetricsReceiver import MetricsReceiver
from dynamite.GENERAL.DynamiteHelper import DYNAMITE_ENVIRONMENT_STRUCT
from dynamite.GENERAL.ServiceEndpoint import ServiceEndpoint
from dynamite.ENGINE.ScalingEngine import ScalingEngine
from dynamite.ENGINE.ScalingEngineConfiguration import ScalingEngineConfiguration
from dynamite.EXECUTOR.DynamiteEXECUTOR import DynamiteEXECUTOR
from dynamite.METRICS.DynamiteMETRICS import DynamiteMETRICS
from dynamite.GENERAL.ScalingMessageSenderReceiverFactory import CommunicationType, ScalingMessageSenderReceiverFactory


class Dynamite:

    DYNAMITE_ENVIRONMENT = os.getenv('DYNAMITE_ENVIRONMENT', DYNAMITE_ENVIRONMENT_STRUCT.DEVELOPMENT)

    DEFAULT_CONFIG_PATH = None
    DEFAULT_SERVICE_FOLDER = None
    DEFAULT_ETCD_ENDPOINT = "127.0.0.1:4001"

    _command_line_arguments = None
    _message_sender_receiver_factory = None

    _scaling_engine_metrics_communication_queue = None
    _exit_flag = None

    def __init__(self):
        self._logger = logging.getLogger("dynamite.Dynamite")
        self._scaling_engine_metrics_communication_queue = None
        self._exit_flag = Value('i', 0)

    def run(self):
        self._logger.info("Started dynamite")
        self.init_env()
        self.init_arguments()
        config = self.parse_config()
        self.create_communication_queues()
        try:
            self.start_executor()
            self.start_metrics_component()
            self.start_scaling_engine(config)
        finally:
            self._exit_flag.value = 1
        self._dynamite_metrics.join()
        self._dynamite_executor.join()

    def init_env(self):
        if platform.system() == 'Windows':
            self._logger.debug("Platform is Windows")
            self._logger.debug("Environment is %s", str(self.DYNAMITE_ENVIRONMENT))
            if self.DYNAMITE_ENVIRONMENT == DYNAMITE_ENVIRONMENT_STRUCT.PRODUCTION:
                self.DEFAULT_CONFIG_PATH = 'C:\\Program Files\\Dynamite\\config.yaml'
                self.DEFAULT_SERVICE_FOLDER = 'C:\\Program Files\\Dynamite\\Service-Files'
            elif self.DYNAMITE_ENVIRONMENT == DYNAMITE_ENVIRONMENT_STRUCT.DEVELOPMENT:
                self.DEFAULT_CONFIG_PATH = os.path.dirname(os.path.realpath(__file__)) \
                                      + '\\tests\\TEST_CONFIG_FOLDER\\config.yaml'
                self.DEFAULT_SERVICE_FOLDER = os.path.dirname(os.path.realpath(__file__)) \
                                              + '\\tests\\TEST_CONFIG_FOLDER\\service-files'
        elif platform.system() == 'Linux' or platform.system() == 'Darwin':
            self._logger.debug("Platform is " + platform.system())
            self._logger.debug("Environment is %s", str(self.DYNAMITE_ENVIRONMENT))

            if self.DYNAMITE_ENVIRONMENT == DYNAMITE_ENVIRONMENT_STRUCT.PRODUCTION:
                self.DEFAULT_CONFIG_PATH = '/etc/dynamite/config.yaml'
                self.DEFAULT_SERVICE_FOLDER = '/etc/dynamite/service-files'
            elif self.DYNAMITE_ENVIRONMENT == DYNAMITE_ENVIRONMENT_STRUCT.DEVELOPMENT:
                self.DEFAULT_CONFIG_PATH = os.path.dirname(os.path.realpath(__file__)) \
                                      + '/tests/TEST_CONFIG_FOLDER/config.yaml'
                self.DEFAULT_SERVICE_FOLDER = os.path.dirname(os.path.realpath(__file__)) \
                                         + '/tests/TEST_CONFIG_FOLDER/service-files'

        self._logger.info("Default config path is %s", self.DEFAULT_CONFIG_PATH)
        self._logger.info("Default service folder path is %s", self.DEFAULT_SERVICE_FOLDER)

    def init_arguments(self):
        parser = argparse.ArgumentParser()

        parser.add_argument("--config_file", "-c",
                            help="Define Config-File to be used. Default: " + self.DEFAULT_CONFIG_PATH,
                            nargs='?',
                            default=self.DEFAULT_CONFIG_PATH)

        parser.add_argument("--service_folder", "-s",
                            help="Define Folder(s) in which dynamite searches for service-files (fleet). Default: " + self.DEFAULT_SERVICE_FOLDER + ". Can be provided multiple times",
                            nargs='?',
                            action='append')

        parser.add_argument("--etcd_endpoint", "-e",
                            help="Define ETCD Endpoint [IP]:[PORT]. Default: " + self.DEFAULT_ETCD_ENDPOINT,
                            nargs='?',
                            default=self.DEFAULT_ETCD_ENDPOINT)

        parser.add_argument("--rabbitmq_endpoint", "-r",
                            help="Define Rabbit-MQ Endpoint [IP]:[PORT].",
                            nargs='?',
                            default=None)
        parser.add_argument("--fleet_endpoint", "-f",
                            help="Define Fleet Endpoint [IP]:[PORT].",
                            nargs='?',
                            default="127.0.0.1:49153")

        args = parser.parse_args()
        self._command_line_arguments = CommandLineArguments(args)
        self._command_line_arguments.log_arguments()

        # Test if Config-File exists. If not, terminate application
        if not os.path.exists(self._command_line_arguments.config_path):
            raise FileNotFoundError(
                "--config-file: {} --> File at given config-path does not exist".format(
                    self._command_line_arguments.config_path
                )
            )

        ARG_SERVICE_FOLDER_TMP = self._command_line_arguments.service_folder if self._command_line_arguments.service_folder is not None else [self.DEFAULT_SERVICE_FOLDER]
        self._command_line_arguments.service_folder = []

        # First test if Service-Folder(s) exist. If not, terminate application
        # If folder(s) exist save the absolute path
        for service_file_folder in ARG_SERVICE_FOLDER_TMP:
            if not os.path.isdir(service_file_folder):
                raise NotADirectoryError("--service-folder: " + service_file_folder + " --> Is not a directory")
            if os.path.isabs(service_file_folder):
                self._command_line_arguments.service_folder.append(service_file_folder)
            else:
                self._command_line_arguments.service_folder.append(os.path.abspath(service_file_folder))

        self._logger.info("Using service folders %s", str(self._command_line_arguments.service_folder))

    def create_communication_queues(self):
        communication_type = CommunicationType.InterProcessQueue
        service_endpoint = None
        if self._command_line_arguments.rabbitmq_endpoint is not None:
            communication_type = CommunicationType.RabbitMQ
            service_endpoint = ServiceEndpoint.from_string(self._command_line_arguments.rabbitmq_endpoint)

        self._message_sender_receiver_factory = ScalingMessageSenderReceiverFactory(communication_type)
        self._message_sender_receiver_factory.initialize_connection(service_endpoint=service_endpoint)
        self._scaling_engine_metrics_communication_queue = Queue()

    def parse_config(self):
        return DynamiteINIT(self._command_line_arguments)

    def start_executor(self):
        scaling_response_sender = self._message_sender_receiver_factory.create_response_sender()
        scaling_request_receiver = self._message_sender_receiver_factory.create_request_receiver()

        self._dynamite_executor = DynamiteEXECUTOR(
            scaling_request_receiver,
            scaling_response_sender,
            self._exit_flag,
            etcd_endpoint=self._command_line_arguments.etcd_endpoint
        )
        self._dynamite_executor.daemon = True
        self._dynamite_executor.start()

    def start_metrics_component(self):
        self._dynamite_metrics = DynamiteMETRICS(
            self._command_line_arguments.etcd_endpoint,
            self._scaling_engine_metrics_communication_queue,
            self._exit_flag
        )
        self._dynamite_metrics.daemon = True
        self._dynamite_metrics.start()

    def start_scaling_engine(self, config):
        scaling_engine_config = ScalingEngineConfiguration()
        scaling_engine_config.metrics_receiver = MetricsReceiver(self._scaling_engine_metrics_communication_queue)
        scaling_engine_config.services_dictionary = config.dynamite_service_handler.FleetServiceDict
        scaling_engine_config.scaling_policies = config.dynamite_config.ScalingPolicy.get_scaling_policies()
        scaling_engine_config.etcd_connection = config.etcdctl

        scaling_engine_config.executed_task_receiver = self._message_sender_receiver_factory.create_response_receiver()
        scaling_engine_config.scaling_action_sender = self._message_sender_receiver_factory.create_request_sender()

        self._scaling_engine = ScalingEngine(scaling_engine_config, self._exit_flag)
        self._scaling_engine.start()

def main():
    dynamite = Dynamite()
    dynamite.run()

if __name__ == '__main__':
    main()
