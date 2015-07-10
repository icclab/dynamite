__author__ = 'bloe'

import pika
import logging

from dynamite.EXECUTOR.DynamiteScalingRequest import DynamiteScalingRequest

class RabbitMQScalingRequestReceiver:

    def __init__(self, rabbit_mq_endpoint, queue_name):
        self._queue_name = queue_name
        self._rabbit_mq_connection_parameters = pika.ConnectionParameters(host=rabbit_mq_endpoint.host_ip,
                                                                port=rabbit_mq_endpoint.port)

    def _on_message_processed(self, delivery_tag):
        self._logger.debug("Send message ack to rabbitmq with tag %s", delivery_tag)
        self._queue_channel.basic_ack(delivery_tag=delivery_tag)

    def connect(self):
        self._logger.debug("Create connection to rabbitmq %s to queue %s", self._rabbit_mq_connection_parameters, self._queue_name)
        self._queue_connection = pika.BlockingConnection(self._rabbit_mq_connection_parameters)
        self._queue_channel = self._queue_connection.channel()

    def receive(self):
        if self._queue_channel is None:
            raise ValueError("You need to connect before you can receive any message!")

        method_frame, header_frame, message_body = self._queue_channel.basic_get(
            queue=self._queue_name,
            no_ack=False
        )
        if self._no_message_delivered(method_frame, header_frame):
            self._logger.debug("Received no scaling request")
            return None

        received_scaling_request_string = message_body.decode("utf-8")

        message_processed_callback = lambda: self._on_message_processed(method_frame.delivery_tag)

        scaling_request = DynamiteScalingRequest.from_json_string(
            received_scaling_request_string,
            message_processed_callback=message_processed_callback
        )
        self._logger.debug("Received scaling request:{:s}".format(received_scaling_request_string))

        return scaling_request

    def _no_message_delivered(self, method_frame, header_frame):
        return method_frame is None or header_frame is None

    def close(self):
        if self._queue_channel is None:
            return

        self._logger.debug("Closing connection to rabbitmq")
        self._queue_connection.close()

    def _get_logger(self):
        return logging.getLogger(__name__)

    _logger = property(_get_logger)
