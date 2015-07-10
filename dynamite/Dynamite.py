#!/usr/bin/env python3

__author__ = 'brnr'

import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

import argparse
import platform
import pika
import logging

from multiprocessing import Queue

from dynamite.INIT.DynamiteINIT import DynamiteINIT
from dynamite.GENERAL.MetricsReceiver import MetricsReceiver
from dynamite.GENERAL.DynamiteHelper import DYNAMITE_ENVIRONMENT_STRUCT
from dynamite.GENERAL.ServiceEndpoint import ServiceEndpoint
from dynamite.ENGINE.ScalingEngine import ScalingEngine
from dynamite.ENGINE.ScalingEngineConfiguration import ScalingEngineConfiguration
from dynamite.EXECUTOR.DynamiteEXECUTOR import DynamiteEXECUTOR
from dynamite.METRICS.DynamiteMETRICS import DynamiteMETRICS

class Dynamite:

    DYNAMITE_ENVIRONMENT = os.getenv('DYNAMITE_ENVIRONMENT', DYNAMITE_ENVIRONMENT_STRUCT.DEVELOPMENT)

    DEFAULT_CONFIG_PATH = None
    DEFAULT_SERVICE_FOLDER = None
    DEFAULT_ETCD_ENDPOINT = "127.0.0.1:4001"
    DEFAULT_RABBITMQ_ENDPOINT = "127.0.0.1:5672"

    ARG_CONFIG_PATH = None
    ARG_SERVICE_FOLDER = None
    ARG_ETCD_ENDPOINT = None
    ARG_RABBITMQ_ENDPOINT = None

    RABBITMQ_SCALING_REQUEST_QUEUE_NAME = "dynamite_scaling_request"
    RABBITMQ_SCALING_RESPONSE_QUEUE_NAME = "dynamite_scaling_response"

    def __init__(self):
        self._logger = logging.getLogger("dynamite.Dynamite")
        pass

    def run(self):
        self._logger.info("Started dynamite")
        self.init_env()
        self.init_arguments()
        config = self.parse_config()
        self.create_rabbit_mq_queues(self.ARG_RABBITMQ_ENDPOINT)
        scaling_engine_metrics_communication_queue = Queue()
        self.start_executor()
        self.start_metrics_component(scaling_engine_metrics_communication_queue)
        self.start_scaling_engine(scaling_engine_metrics_communication_queue, config)

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
                            help="Define Rabbit-MQ Endpoint [IP]:[PORT]. Default: " + self.DEFAULT_RABBITMQ_ENDPOINT,
                            nargs='?',
                            default=self.DEFAULT_RABBITMQ_ENDPOINT)

        args = parser.parse_args()

        self.ARG_ETCD_ENDPOINT = args.etcd_endpoint
        self.ARG_CONFIG_PATH = args.config_file
        self.ARG_RABBITMQ_ENDPOINT = args.rabbitmq_endpoint

        self._logger.info("Using ectd endpoint %s", self.ARG_ETCD_ENDPOINT)
        self._logger.info("Using config path %s", self.ARG_CONFIG_PATH)
        self._logger.info("Using rabbitmq endpoint %s", self.ARG_RABBITMQ_ENDPOINT)

        # Test if Config-File exists. If not, terminate application
        if not os.path.exists(self.ARG_CONFIG_PATH):
            raise FileNotFoundError("--config-file: " + self.ARG_CONFIG_PATH + " --> File at given config-path does not exist")

        ARG_SERVICE_FOLDER_TMP = args.service_folder if args.service_folder is not None else [self.DEFAULT_SERVICE_FOLDER]
        self.ARG_SERVICE_FOLDER = []

        # First test if Service-Folder(s) exist. If not, terminate application
        # If folder(s) exist save the absolute path
        for service_file_folder in ARG_SERVICE_FOLDER_TMP:
            if not os.path.isdir(service_file_folder):
                raise NotADirectoryError("--service-folder: " + service_file_folder + " --> Is not a directory")
            if os.path.isabs(service_file_folder):
                self.ARG_SERVICE_FOLDER.append(service_file_folder)
            else:
                self.ARG_SERVICE_FOLDER.append(os.path.abspath(service_file_folder))

        self._logger.info("Using service folders %s", str(self.ARG_SERVICE_FOLDER))

    def create_rabbit_mq_queues(self, rabbit_mq_endpoint_string):

        self._logger.debug("Connection to rabbitmq %s", rabbit_mq_endpoint_string)
        rabbit_mq_endpoint = ServiceEndpoint.from_string(rabbit_mq_endpoint_string)
        rabbit_mq_connection_parameters = pika.ConnectionParameters(host=rabbit_mq_endpoint.host_ip,
                                                                    port=rabbit_mq_endpoint.port)

        connection = pika.BlockingConnection(rabbit_mq_connection_parameters)
        channel = connection.channel()

        self._logger.debug("Creating scaling request queue %s", self.RABBITMQ_SCALING_REQUEST_QUEUE_NAME)
        channel.queue_declare(queue=self.RABBITMQ_SCALING_REQUEST_QUEUE_NAME, durable=True)
        self._logger.debug("Creating scaling response queue %s", self.RABBITMQ_SCALING_RESPONSE_QUEUE_NAME)
        channel.queue_declare(queue=self.RABBITMQ_SCALING_RESPONSE_QUEUE_NAME, durable=True)

        connection.close()

    def parse_config(self):
        return DynamiteINIT(self.ARG_CONFIG_PATH, self.ARG_SERVICE_FOLDER, self.ARG_ETCD_ENDPOINT)

    def start_executor(self):
        dynamite_executor = DynamiteEXECUTOR(rabbit_mq_endpoint=self.ARG_RABBITMQ_ENDPOINT,
                                             etcd_endpoint=self.ARG_ETCD_ENDPOINT,
                                             name_scaling_request_queue=self.RABBITMQ_SCALING_REQUEST_QUEUE_NAME,
                                             name_scaling_response_queue=self.RABBITMQ_SCALING_RESPONSE_QUEUE_NAME)

        dynamite_executor.start()

    def start_metrics_component(self, scaling_engine_metrics_communication_queue):
        dynamite_metrics = DynamiteMETRICS(self.ARG_ETCD_ENDPOINT,
                                           scaling_engine_metrics_communication_queue)
        dynamite_metrics.start()

    def start_scaling_engine(self, scaling_engine_metrics_communication_queue, config):
        scaling_engine_config = ScalingEngineConfiguration()
        scaling_engine_config.metrics_receiver = MetricsReceiver(scaling_engine_metrics_communication_queue)
        scaling_engine_config.services_dictionary = config.dynamite_service_handler.FleetServiceDict
        scaling_engine_config.scaling_policies = config.dynamite_config.ScalingPolicy.get_scaling_policies()
        scaling_engine_config.etcd_connection = config.etcdctl
        scaling_engine_config.rabbit_mq_endpoint = ServiceEndpoint.from_string(self.ARG_RABBITMQ_ENDPOINT)
        scaling_engine_config.scaling_request_queue_name = self.RABBITMQ_SCALING_REQUEST_QUEUE_NAME
        scaling_engine_config.scaling_response_queue_name = self.RABBITMQ_SCALING_RESPONSE_QUEUE_NAME

        scaling_engine = ScalingEngine(scaling_engine_config)
        scaling_engine.start()

def main():
    dynamite = Dynamite()
    dynamite.run()

if __name__ == '__main__':
    main()
