__author__ = 'bloe'

import time
from dynamite import Dynamite
from dynamite.GENERAL.ServiceEndpoint import ServiceEndpoint
from dynamite.ENGINE.RabbitMQScalingActionSender import RabbitMQScalingActionSender
from dynamite.EXECUTOR.DynamiteScalingRequest import DynamiteScalingRequest
from dynamite.EXECUTOR.DynamiteScalingCommand import DynamiteScalingCommand

import pika

class TestScalingActionSender(Dynamite.Dynamite):

    RABBIT_MQ_ENDPOINT = "127.0.0.1:5672"

    def run(self):
        self.init_env()
        self.init_arguments()
        config = self.parse_config()

        rabbit_mq_endpoint = ServiceEndpoint.from_string(self.RABBIT_MQ_ENDPOINT)
        self._connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbit_mq_endpoint.host_ip, port=rabbit_mq_endpoint.port)
        )
        self._channel = self._connection.channel()

        self.delete_queue()
        self.create_rabbit_mq_queues(self._rabbitmq_endpoint_argument)

        self._scaling_action_sender = RabbitMQScalingActionSender(
            rabbit_mq_endpoint,
            self.RABBITMQ_SCALING_REQUEST_QUEUE_NAME
        )

        content = self.create_content()
        self.send_content(content)
        time.sleep(2)
        self.check_if_content_in_queue(content)

        self._scaling_action_sender.close()

    def delete_queue(self):
        self._channel.queue_delete(queue=self.RABBITMQ_SCALING_REQUEST_QUEUE_NAME)

    def send_content(self, content):
        self._scaling_action_sender.send_action(content[0])
        self._scaling_action_sender.send_action(content[1])

    def create_content(self):
        content = []

        request = DynamiteScalingRequest()
        request.command = DynamiteScalingCommand.SCALE_DOWN
        request.failure_counter = 2
        request.service_instance_name = "apache_service_instance_name_1"
        request.service_name = "apache_service_name"
        content.append(request)

        request = DynamiteScalingRequest()
        request.command = DynamiteScalingCommand.SCALE_UP
        request.failure_counter = 0
        request.service_instance_name = "apache_service_instance_name_2"
        request.service_name = "apache_service_name"
        content.append(request)
        return content

    def check_if_content_in_queue(self, content):
        for content_message in content:
            method_frame, header_frame, message_body = self._channel.basic_get(queue=self.RABBITMQ_SCALING_REQUEST_QUEUE_NAME, no_ack=False)
            request = DynamiteScalingRequest.from_json_string(message_body.decode("utf-8"))
            success_or_error = "[SUCCESS]" if request == content_message else "[ERROR]"
            print("{} Received message {}".format(success_or_error, message_body))

if __name__ == '__main__':
    dynamite = TestScalingActionSender()
    dynamite.run()
