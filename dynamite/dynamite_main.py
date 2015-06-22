__author__ = 'brnr'

import sys
import argparse
import os
import platform
import pika

from multiprocessing import Queue

from dynamite.INIT.DynamiteINIT import DynamiteINIT
from dynamite.GENERAL.MetricsReceiver import MetricsReceiver
from dynamite.GENERAL.DynamiteHelper import DYNAMITE_ENVIRONMENT_STRUCT
from dynamite.GENERAL.ServiceEndpoint import ServiceEndpoint
from dynamite.ENGINE.ScalingEngine import ScalingEngine
from dynamite.ENGINE.ScalingEngineConfiguration import ScalingEngineConfiguration
from dynamite.EXECUTOR.DynamiteEXECUTOR import DynamiteEXECUTOR
from dynamite.METRICS.DynamiteMETRICS import DynamiteMETRICS

WORKING_DIRECTORY = 'C:\\Projects\\CNA\\dynamite'

# The following is only for usage of this application from the command-line
# And only during development
# The application should later be installed via setup.py
if WORKING_DIRECTORY not in sys.path:
    sys.path.append(WORKING_DIRECTORY)

if WORKING_DIRECTORY not in sys.path:
    sys.path.append(WORKING_DIRECTORY)

DYNAMITE_ENVIRONMENT = os.getenv('DYNAMITE_ENVIRONMENT', DYNAMITE_ENVIRONMENT_STRUCT.DEVELOPMENT)

DEFAULT_CONFIG_PATH=None
DEFAULT_SERVICE_FOLDER=None
DEFAULT_ETCD_ENDPOINT="127.0.0.1:4001"
DEFAULT_RABBITMQ_ENDPOINT="127.0.0.1:5672"

ARG_CONFIG_PATH=None
ARG_SERVICE_FOLDER=None
ARG_ETCD_ENDPOINT=None
ARG_RABBITMQ_ENDPOINT=None

RABBITMQ_SCALING_REQUEST_QUEUE_NAME="dynamite_scaling_request"
RABBITMQ_SCALING_RESPONSE_QUEUE_NAME="dynamite_scaling_response"

def init_env():
    global DEFAULT_CONFIG_PATH
    global DEFAULT_SERVICE_FOLDER

    if platform.system() == 'Windows':
        if DYNAMITE_ENVIRONMENT == DYNAMITE_ENVIRONMENT_STRUCT.PRODUCTION:
            DEFAULT_CONFIG_PATH = 'C:\\Program Files\\Dynamite\\config.yaml'
            DEFAULT_SERVICE_FOLDER = 'C:\\Program Files\\Dynamite\\Service-Files'
        elif DYNAMITE_ENVIRONMENT == DYNAMITE_ENVIRONMENT_STRUCT.DEVELOPMENT:
            DEFAULT_CONFIG_PATH = 'tests\\TEST_CONFIG_FOLDER\\config.yaml'
            DEFAULT_SERVICE_FOLDER = 'tests\\TEST_CONFIG_FOLDER\\service-files'
    elif platform.system()() == 'Linux':
        DEFAULT_CONFIG_PATH = '/etc/dynamite/config.yaml'
        DEFAULT_SERVICE_FOLDER = '/etc/dynamite/service-files'


def init_arguments():
    global ARG_CONFIG_PATH
    global ARG_SERVICE_FOLDER
    global ARG_ETCD_ENDPOINT
    global ARG_RABBITMQ_ENDPOINT

    parser = argparse.ArgumentParser()

    parser.add_argument("--config_file", "-c",
                        help="Define Config-File to be used. Default: " + DEFAULT_CONFIG_PATH,
                        nargs='?',
                        default=DEFAULT_CONFIG_PATH)

    parser.add_argument("--service_folder", "-s",
                        help="Define Folder(s) in which dynamite searches for service-files (fleet). Default: " + DEFAULT_SERVICE_FOLDER + ". Can be provided multiple times",
                        nargs='?',
                        action='append')

    parser.add_argument("--etcd_endpoint", "-e",
                        help="Define ETCD Endpoint [IP]:[PORT]. Default: " + DEFAULT_ETCD_ENDPOINT,
                        nargs='?',
                        default=DEFAULT_ETCD_ENDPOINT)

    parser.add_argument("--rabbitmq_endpoint", "-r",
                        help="Define Rabbit-MQ Endpoint [IP]:[PORT]. Default: " + DEFAULT_RABBITMQ_ENDPOINT,
                        nargs='?',
                        default=DEFAULT_RABBITMQ_ENDPOINT)

    args = parser.parse_args()

    ARG_ETCD_ENDPOINT = args.etcd_endpoint

    ARG_CONFIG_PATH = args.config_file

    ARG_RABBITMQ_ENDPOINT = args.rabbitmq_endpoint

    # Test if Config-File exists. If not, terminate application
    if not os.path.exists(ARG_CONFIG_PATH):
        raise FileNotFoundError("--config-file: " + ARG_CONFIG_PATH + " --> File at given config-path does not exist")

    ARG_SERVICE_FOLDER_TMP = args.service_folder if args.service_folder != None else [DEFAULT_SERVICE_FOLDER]

    ARG_SERVICE_FOLDER = []

    # First test if Service-Folder(s) exist. If not, terminate application
    # If folder(s) exist save the absolute path
    for service_file_folder in ARG_SERVICE_FOLDER_TMP:
        if not os.path.isdir(service_file_folder):
            raise NotADirectoryError("--service-folder: " + service_file_folder + " --> Is not a directory")
        if os.path.isabs(service_file_folder):
            ARG_SERVICE_FOLDER.append(service_file_folder)
        else:
            ARG_SERVICE_FOLDER.append(os.path.abspath(service_file_folder))


def create_rabbit_mq_queues(rabbit_mq_endpoint):

    ip_port = rabbit_mq_endpoint.split(":")
    rabbit_mq_endpoint_host = ip_port[0]
    rabbit_mq_endpoint_port = int(ip_port[1])

    rabbit_mq_connection_parameters = pika.ConnectionParameters(host=rabbit_mq_endpoint_host,
                                                                port=rabbit_mq_endpoint_port)

    connection = pika.BlockingConnection(rabbit_mq_connection_parameters)

    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_SCALING_REQUEST_QUEUE_NAME, durable=True)
    channel.queue_declare(queue=RABBITMQ_SCALING_RESPONSE_QUEUE_NAME, durable=True)

    connection.close()


if __name__ == '__main__':
    init_env()
    init_arguments()

    dynamite_init = DynamiteINIT(ARG_CONFIG_PATH, ARG_SERVICE_FOLDER, ARG_ETCD_ENDPOINT)

    create_rabbit_mq_queues(ARG_RABBITMQ_ENDPOINT)

    dynamite_executor = DynamiteEXECUTOR(rabbit_mq_endpoint=ARG_RABBITMQ_ENDPOINT,
                                         etcd_endpoint=ARG_ETCD_ENDPOINT,
                                         name_scaling_request_queue=RABBITMQ_SCALING_REQUEST_QUEUE_NAME,
                                         name_scaling_response_queue=RABBITMQ_SCALING_RESPONSE_QUEUE_NAME)

    dynamite_executor.start()

    scaling_engine_metrics_communication_queue = Queue()
    dynamite_metrics = DynamiteMETRICS(ARG_ETCD_ENDPOINT,
                                       scaling_engine_metrics_communication_queue)

    dynamite_metrics.start()

    scaling_engine_config = ScalingEngineConfiguration()
    scaling_engine_config.metrics_receiver = MetricsReceiver(scaling_engine_metrics_communication_queue)
    scaling_engine_config.services_dictionary = dynamite_init.dynamite_service_handler.FleetServiceDict
    scaling_engine_config.scaling_policies = dynamite_init.dynamite_config.ScalingPolicy.get_scaling_policies()
    scaling_engine_config.etcd_connection = dynamite_init.etcdctl
    scaling_engine_config.rabbit_mq_endpoint = ServiceEndpoint.from_string(ARG_RABBITMQ_ENDPOINT)
    scaling_engine_config.scaling_request_queue_name = RABBITMQ_SCALING_REQUEST_QUEUE_NAME
    scaling_engine_config.scaling_response_queue_name = RABBITMQ_SCALING_RESPONSE_QUEUE_NAME

    scaling_engine = ScalingEngine(scaling_engine_config)
    scaling_engine.start()
