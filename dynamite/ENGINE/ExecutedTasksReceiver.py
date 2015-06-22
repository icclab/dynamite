__author__ = 'bloe'

import pika

from dynamite.EXECUTOR.DynamiteScalingResponse import DynamiteScalingResponse

class ExecutedTaskReceiver(object):
    def __init__(self, rabbit_mq_endpoint, queue_name):
        self._queue_name = queue_name
        rabbit_mq_connection_parameters = pika.ConnectionParameters(host=rabbit_mq_endpoint.host_ip,
                                                                    port=rabbit_mq_endpoint.port)
        self._queue_connection = pika.BlockingConnection(rabbit_mq_connection_parameters)
        self._queue_channel = self.rabbit_mq_connection.channel()

    def receive(self):
        messages = ()
        method_frame, header_frame, message_body = self._queue_channel.basic_get(queue=self._queue_name, no_ack=False)
        if self._no_message_delivered(method_frame, header_frame):
            return messages

        received_scaling_response_string = message_body.decode("utf-8")
        scaling_response = DynamiteScalingResponse.from_json_string(received_scaling_response_string)
        messages = (scaling_response,)
        return messages + self.receive()

    def _no_message_delivered(self, method_frame, header_frame):
        return method_frame is None or header_frame is None

    def close(self):
        self._queue_connection.close()
