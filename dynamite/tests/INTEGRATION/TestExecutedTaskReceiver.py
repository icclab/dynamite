__author__ = 'bloe'

from dynamite.ENGINE.RabbitMQExecutedTaskReceiver import RabbitMQExecutedTaskReceiver
from dynamite import Dynamite
from dynamite.GENERAL.ServiceEndpoint import ServiceEndpoint
from dynamite.EXECUTOR.DynamiteScalingResponse import DynamiteScalingResponse
from dynamite.EXECUTOR.DynamiteScalingCommand import DynamiteScalingCommand
import pika
import time

class TestExecutedTaskReceiver(Dynamite.Dynamite):

    RABBIT_MQ_ENDPOINT = "127.0.0.1:5672"

    def __init__(self):
        super(TestExecutedTaskReceiver, self).__init__()

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

        self._task_receiver = RabbitMQExecutedTaskReceiver(
            rabbit_mq_endpoint,
            self.RABBITMQ_SCALING_RESPONSE_QUEUE_NAME
        )

        self.receive_empty()
        self.write_content_to_queue()
        time.sleep(2)
        self.receive_content()

        self._task_receiver.close()

    def delete_queue(self):
        self._channel.queue_delete(queue=self.RABBITMQ_SCALING_RESPONSE_QUEUE_NAME)

    def receive_empty(self):
        received_messages = self._task_receiver.receive()
        if len(received_messages) == 0:
            print("[SUCCESS] Received empty message")
        else:
            print("[ERROR] Did not receive empty message")
            for received_message in received_messages:
                print("Received: {}".format(received_message))

    def write_content_to_queue(self):
        for response in self.create_content():
            self._channel.basic_publish(exchange='',
                                  routing_key=self.RABBITMQ_SCALING_RESPONSE_QUEUE_NAME,
                                  body=response.to_json_string())

    def create_content(self):
        content = []

        response = DynamiteScalingResponse()
        response.command = DynamiteScalingCommand.SCALE_DOWN
        response.failure_counter = 2
        response.service_instance_name = "apache_service_instance_name"
        response.service_name = "apache_service_name"
        response.success = True
        content.append(response)

        response = DynamiteScalingResponse()
        response.command = DynamiteScalingCommand.SCALE_UP
        response.failure_counter = 0
        response.service_instance_name = "apache_service_instance_name"
        response.service_name = "apache_service_name"
        response.success = False
        content.append(response)
        return content

    def receive_content(self):
        expected_message_count = len(self.create_content())
        received_messages = self._task_receiver.receive()
        received_message_count = len(received_messages)
        error_or_success = "[SUCCESS]" if expected_message_count == received_message_count else "[ERROR]"
        print("{} Messages Received: Expected {}, Received {}".format(error_or_success, expected_message_count, received_message_count))
        for received_message in received_messages:
            print("\t Received: {}".format(received_message))

if __name__ == '__main__':
    dynamite = TestExecutedTaskReceiver()
    dynamite.run()
