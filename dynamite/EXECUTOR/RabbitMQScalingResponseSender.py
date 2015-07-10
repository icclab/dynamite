__author__ = 'bloe'

import logging
import pika

class RabbitMQScalingResponseSender:
    def __init__(self, rabbit_mq_endpoint, queue_name):
        self._rabbit_mq_connection_parameters = pika.ConnectionParameters(host=rabbit_mq_endpoint.host_ip,
                                                                    port=rabbit_mq_endpoint.port)
        self._queue_name = queue_name

    def connect(self):
        self._logger.debug("Create connection to rabbitmq %s to queue %s", repr(self._rabbit_mq_connection_parameters), self._queue_name)
        self._rabbit_mq_connection = pika.BlockingConnection(self._rabbit_mq_connection_parameters)
        self._queue_channel = self._rabbit_mq_connection.channel()

    def send_response(self, scaling_response):
        if self._queue_channel is None:
            raise ValueError("You need to connect before you can send any message!")

        self._logger.info("Sending scaling response %s to rabbitmq", repr(scaling_response))
        scaling_response_string = scaling_response.to_json_string()
        self._queue_channel.basic_publish(exchange='',
                                          routing_key=self._queue_name,
                                          body=scaling_response_string)

    def close(self):
        if self._queue_channel is None:
            return

        self._logger.debug("Closing connection to rabbitmq")
        self._rabbit_mq_connection.close()

    def _get_logger(self):
        return logging.getLogger(__name__)

    _logger = property(_get_logger)
