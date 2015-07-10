__author__ = 'bloe'

import pika
import logging
from enum import Enum
from multiprocessing import Queue

from dynamite.ENGINE.ExecutedTasksReceiver import ExecutedTaskReceiver
from dynamite.ENGINE.ScalingActionSender import ScalingActionSender
from dynamite.ENGINE.RabbitMQExecutedTaskReceiver import RabbitMQExecutedTaskReceiver
from dynamite.ENGINE.RabbitMQScalingActionSender import RabbitMQScalingActionSender
from dynamite.EXECUTOR.RabbitMQScalingRequestReceiver import RabbitMQScalingRequestReceiver
from dynamite.EXECUTOR.RabbitMQScalingResponseSender import RabbitMQScalingResponseSender
from dynamite.EXECUTOR.ScalingResponseSender import ScalingResponseSender
from dynamite.EXECUTOR.ScalingRequestReceiver import ScalingRequestReceiver

class CommunicationType(Enum):
    RabbitMQ = 1,
    InterProcessQueue = 2


class ScalingMessageSenderReceiverFactory:

    _factory = None

    def __init__(self, communication_type):
        if communication_type == CommunicationType.InterProcessQueue:
            self._factory = ProcessQueueScalingMessageSenderReceiverFactory()
        elif communication_type == CommunicationType.RabbitMQ:
            self._factory = RabbitMQScalingMessageSenderReceiverFactory()
        else:
            raise ValueError("Unknown or unsupported type {}".format(communication_type))

    def initialize_connection(self, service_endpoint=None):
        self._factory.initialize_connection(service_endpoint=service_endpoint)

    def create_request_receiver(self):
        return self._factory.create_request_receiver()

    def create_request_sender(self):
        return self._factory.create_request_sender()

    def create_response_sender(self):
        return self._factory.create_response_sender()

    def create_response_receiver(self):
        return self._factory.create_response_receiver()


class RabbitMQScalingMessageSenderReceiverFactory:

    RABBITMQ_SCALING_REQUEST_QUEUE_NAME = "dynamite_scaling_request"
    RABBITMQ_SCALING_RESPONSE_QUEUE_NAME = "dynamite_scaling_response"

    _rabbitmq_endpoint = None

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def initialize_connection(self, service_endpoint):
        self._rabbitmq_endpoint = service_endpoint
        self._logger.debug("Connection to rabbitmq %s", service_endpoint)
        rabbit_mq_connection_parameters = pika.ConnectionParameters(
            host=self._rabbitmq_endpoint.host_ip,
            port=self._rabbitmq_endpoint.port
        )

        connection = pika.BlockingConnection(rabbit_mq_connection_parameters)
        channel = connection.channel()

        self._logger.debug("Creating scaling request queue %s", self.RABBITMQ_SCALING_REQUEST_QUEUE_NAME)
        channel.queue_declare(queue=self.RABBITMQ_SCALING_REQUEST_QUEUE_NAME, durable=True)
        self._logger.debug("Creating scaling response queue %s", self.RABBITMQ_SCALING_RESPONSE_QUEUE_NAME)
        channel.queue_declare(queue=self.RABBITMQ_SCALING_RESPONSE_QUEUE_NAME, durable=True)

        connection.close()

    def create_request_receiver(self):
        return RabbitMQScalingRequestReceiver(
            self._rabbitmq_endpoint,
            self.RABBITMQ_SCALING_REQUEST_QUEUE_NAME
        )

    def create_request_sender(self):
        return RabbitMQScalingActionSender(
            self._rabbitmq_endpoint,
            self.RABBITMQ_SCALING_REQUEST_QUEUE_NAME
        )

    def create_response_sender(self):
        return RabbitMQScalingResponseSender(
                self._rabbitmq_endpoint,
                self.RABBITMQ_SCALING_RESPONSE_QUEUE_NAME
        )

    def create_response_receiver(self):
        return RabbitMQExecutedTaskReceiver(
            self._rabbitmq_endpoint,
            self.RABBITMQ_SCALING_RESPONSE_QUEUE_NAME
        )

class ProcessQueueScalingMessageSenderReceiverFactory:

    _scaling_action_response_communication_queue = None
    _scaling_action_communication_queue = None

    def __init__(self):
        self._logging = logging.getLogger(__name__)

    def initialize_connection(self, service_endpoint=None):
        self._scaling_action_communication_queue = Queue()
        self._scaling_action_response_communication_queue = Queue()

    def create_request_receiver(self):
        return ScalingRequestReceiver(
            self._scaling_action_communication_queue
        )

    def create_request_sender(self):
        return ScalingActionSender(self._scaling_action_communication_queue)

    def create_response_sender(self):
        return ScalingResponseSender(
            self._scaling_action_response_communication_queue
        )

    def create_response_receiver(self):
        return ExecutedTaskReceiver(self._scaling_action_response_communication_queue)
