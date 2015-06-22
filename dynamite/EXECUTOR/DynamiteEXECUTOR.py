__author__ = 'brnr'

from multiprocessing import Process
from dynamite.INIT.DynamiteServiceHandler import DynamiteServiceHandler
from dynamite.INIT.DynamiteConfig import DynamiteConfig

from dynamite.GENERAL.DynamiteExceptions import IllegalArgumentError
from dynamite.EXECUTOR.DynamiteScalingRequest import DynamiteScalingRequest
from dynamite.EXECUTOR.DynamiteScalingResponse import DynamiteScalingResponse
from dynamite.EXECUTOR.DynamiteScalingCommand import DynamiteScalingCommand

import logging
import pika
import atexit


# DynamiteExecutor is a Process which reads scaling request from a rabbitmq queue and creates or deletes fleet-services
# in a CoreOS Cluster

class DynamiteEXECUTOR(Process):

    dynamite_service_handler = None
    dynamite_config = None

    name_scaling_request_queue = "dynamite_scaling_request"
    name_scaling_response_queue = "dynamite_scaling_response"

    rabbit_mq_connection = None
    rabbit_mq_channel = None
    rabbit_mq_endpoint = "127.0.0.1:5672"
    rabbit_mq_endpoint_host = None
    rabbit_mq_endpoint_port = None

    etcd_endpoint = "127.0.0.1:4001"

    dynamite_executor_parameters = None


    def _create_rabbit_mq_connection(self):
        rabbit_mq_host = self.rabbit_mq_endpoint_host
        rabbit_mq_port = self.rabbit_mq_endpoint_port

        rabbit_mq_connection_parameters = pika.ConnectionParameters(host=rabbit_mq_host,
                                                                    port=rabbit_mq_port)

        self.rabbit_mq_connection = pika.BlockingConnection(rabbit_mq_connection_parameters)

        self.rabbit_mq_channel = self.rabbit_mq_connection.channel()

    def _close_rabbit_mq_connection(self):
        if self.rabbit_mq_connection:
            self.rabbit_mq_connection.close()

    def _create_dynamite_config(self, etcd_endpoint):
        self.dynamite_config = DynamiteConfig(etcd_endpoint=etcd_endpoint)

    def _create_dynamite_service_handler(self, dynamite_config, etcd_endpoint):
        self.dynamite_service_handler = DynamiteServiceHandler(dynamite_config=dynamite_config,
                                                               etcd_endpoint=etcd_endpoint)

    def _scaling_request_received(self, ch, method, properties, body):

        received_scaling_request_string = body.decode("utf-8")

        scaling_request = DynamiteScalingRequest.from_json_string(received_scaling_request_string)

        response = None
        if scaling_request.command == DynamiteScalingCommand.SCALE_UP:
            service_name = scaling_request.service_name
            response = self.dynamite_service_handler.add_new_fleet_service_instance(service_name)
        elif scaling_request.command == DynamiteScalingCommand.SCALE_DOWN:
            service_name = scaling_request.service_name
            service_instance_name = scaling_request.service_instance_name
            response = self.dynamite_service_handler.remove_fleet_service_instance(service_name, service_instance_name)

        # TODO: send the response (failure/success) to the response queue
        scaling_success = True if response is not None else False

        scaling_response = DynamiteScalingResponse(scaling_request, scaling_success)

        self._send_scaling_response_to_rabbitmq_response_queue(scaling_response)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def _send_scaling_response_to_rabbitmq_response_queue(self, scaling_response):
        if not isinstance(scaling_response, DynamiteScalingResponse):
            raise IllegalArgumentError("Error: argument <scaling_response needs to be of type "
                                       "dynamite.EXECUTOR.DynamiteScalingResponse")

        scaling_response_string = scaling_response.to_json_string()

        if self.rabbit_mq_channel:
            self.rabbit_mq_channel.basic_publish(exchange='',
                                                 routing_key=self.name_scaling_response_queue,
                                                 body=scaling_response_string)

    def run(self):
        self._create_dynamite_config(self.etcd_endpoint)
        self._create_dynamite_service_handler(self.dynamite_config, self.etcd_endpoint)

        self._create_rabbit_mq_connection()

        if self.rabbit_mq_channel:
            self.rabbit_mq_channel.basic_consume(self._scaling_request_received,
                                                 queue=self.name_scaling_request_queue,
                                                 no_ack=False)

            self.rabbit_mq_channel.start_consuming()

    def __init__(self,
                 rabbit_mq_endpoint=None,
                 etcd_endpoint=None,
                 name_scaling_request_queue=None,
                 name_scaling_response_queue=None):
        super(DynamiteEXECUTOR, self).__init__()

        if etcd_endpoint is not None and isinstance(etcd_endpoint, str):
            self.etcd_endpoint = etcd_endpoint
        else:
            raise IllegalArgumentError("Error: argument <etcd_endpoint> needs to be of type <str>")

        if rabbit_mq_endpoint is not None and isinstance(rabbit_mq_endpoint, str):
            self.rabbit_mq_endpoint = rabbit_mq_endpoint

        ip_port = self.rabbit_mq_endpoint.split(":")
        self.rabbit_mq_endpoint_host = ip_port[0]
        self.rabbit_mq_endpoint_port = int(ip_port[1])

        if name_scaling_request_queue is not None:
            if isinstance(name_scaling_request_queue, str):
                self.name_scaling_request_queue = name_scaling_request_queue
            else:
                raise IllegalArgumentError("Error: argument <name_scaling_request_queue> needs to be of type <str>")

        if name_scaling_response_queue is not None:
            if isinstance(name_scaling_response_queue, str):
                self.name_scaling_response_queue = name_scaling_response_queue
            else:
                raise IllegalArgumentError("Error: argument <name_scaling_response_queue> needs to be of type <str>")

        atexit.register(self._close_rabbit_mq_connection)



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
