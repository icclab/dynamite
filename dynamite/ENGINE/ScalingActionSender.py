__author__ = 'bloe'

import pika

class ScalingActionSender(object):
    def __init__(self, rabbit_mq_endpoint, queue_name):
        rabbit_mq_connection_parameters = pika.ConnectionParameters(host=rabbit_mq_endpoint.host_ip,
                                                                    port=rabbit_mq_endpoint.port)
        self._rabbit_mq_connection = pika.BlockingConnection(rabbit_mq_connection_parameters)
        self._queue_channel = self._rabbit_mq_connection.channel()
        self._queue_name = queue_name

    def send_action(self, scaling_request):
        scaling_request_string = scaling_request.to_json_string()
        self._queue_channel.basic_publish(exchange='',
                                          routing_key=self._queue_name,
                                          body=scaling_request_string)

    def close(self):
        self._rabbit_mq_connection.close()

