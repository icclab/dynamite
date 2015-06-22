__author__ = 'brnr'
import pika
import json
import time

from dynamite.GENERAL.DynamiteExceptions import IllegalArgumentError
from dynamite.EXECUTOR.DynamiteScalingCommand import DynamiteScalingCommand

class ScalingRequestGenerator(object):

    rabbitmq_connection = None
    dynamite_scaling_request = None
    dynamite_scaling_response = None

    def _create_rabbit_mq_connection(self):
        rabbit_mq_host = '127.0.0.1'
        rabbit_mq_port = 5672

        rabbit_mq_connection_parameters = pika.ConnectionParameters(host=rabbit_mq_host,
                                                                    port=rabbit_mq_port)

        rabbit_mq_connection = pika.BlockingConnection(rabbit_mq_connection_parameters)

        return rabbit_mq_connection


    # def _create_scaling_request_string(self, scaling_command, service_name=None, service_instance_name=None):
    #
    #     scaling_request = {
    #         "command": scaling_command,
    #         "service_name": "a",
    #         "service_instance_name": None,
    #         "failure_counter": 0
    #     }
    #
    #     scaling_request_string = json.dumps(scaling_request)
    #
    #     return scaling_request_string

    def generate_scaling_requests(self,
                                  scaling_command,
                                  service_name=None,
                                  service_instance_name=None,
                                  number_of_requests=1):

        if scaling_command not in DynamiteScalingCommand.ALLOWED_COMMANDS:
            raise IllegalArgumentError("Error: argument <scaling_command> needs to either be 'scale_up' or 'scale_down'")

        if not isinstance(number_of_requests, int) and number_of_requests < 1:
            raise IllegalArgumentError("Error: argument <number_of_requests> needs to be of type <int> and can not"
                                       "be less than 1")

        if service_name is not None:
            scaling_request = {
                "command": scaling_command,
                "service_name": service_name,
                "service_instance_name": service_instance_name,
                "failure_counter": 0
            }
        else:
            raise IllegalArgumentError("Error: argument <service_name> needs to always be set")

        scaling_request_string = json.dumps(scaling_request)

        for requests in range(number_of_requests):
            # scaling_request_string = self._create_scaling_request_string(scaling_command)

            self.rabbitmq_channel.basic_publish(exchange='',
                                                routing_key=self.dynamite_scaling_request,
                                                body=scaling_request_string)

            print("sent scaling request " + scaling_request_string + " to queue: " + self.dynamite_scaling_request)

    def close_rabbit_mq_connection(self):
        self.rabbitmq_connection.close()

    def __init__(self):
        self.dynamite_scaling_request = "dynamite_scaling_request"
        self.dynamite_scaling_response = "dynamite_scaling_response"

        self.rabbitmq_connection = self._create_rabbit_mq_connection()

        self.rabbitmq_channel = self.rabbitmq_connection.channel()
        self.rabbitmq_channel.queue_declare(queue=self.dynamite_scaling_request, durable=True)
        self.rabbitmq_channel.queue_declare(queue=self.dynamite_scaling_response, durable=True)

if __name__ == '__main__':
    scaling_request_generator = ScalingRequestGenerator()
    #scaling_request_generator.generate_scaling_requests("scale_up", service_name="a")
    res = scaling_request_generator.generate_scaling_requests("scale_down",
                                                              service_name="a",
                                                              service_instance_name="a@12023.service")

    print(res)

    scaling_request_generator.close_rabbit_mq_connection()

#   Scaling Request
#   {
#       "command": "scale_up / scale_down",
#       "service": "service_name (e.g. zurmo_apache)",
#       "service_instance_name" : "service_instance_name (e.g. zurmo_apache@8080.service)"  --> will only be set when scaling down, otherwise set to 'None'
#       "failure_counter" : <int> --> starts at 0 and is increased when a failure occurs
#   }
#
#   Scaling Response:
#   {
#       "success": "true / false"
#       "command": "scale_up / scale_down",
#       "service": "service_name (e.g. zurmo_apache)",
#       "service_instance_name" : "service_instance_name (e.g. zurmo_apache@8080.service)"  --> will only be set when scaling down, otherwise set to 'None'
#       "failure_counter" : <int> --> starts at 0 and is increased when a failure occurs
#   }
