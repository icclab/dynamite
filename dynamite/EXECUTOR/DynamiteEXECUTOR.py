__author__ = 'brnr'

from multiprocessing import Process
from dynamite.INIT.DynamiteServiceHandler import DynamiteServiceHandler
from dynamite.INIT.DynamiteConfig import DynamiteConfig

from dynamite.GENERAL.DynamiteExceptions import IllegalArgumentError

import logging
import pika
import json

# DynamiteExecutor is a Process which reads scaling request from a rabbitmq queue and creates or deletes fleet-services
# in a CoreOS Cluster
#
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

class DynamiteEXECUTOR(Process):

    dynamite_service_handler = None
    dynamite_config = None

    name_scaling_request_queue = "dynamite_scaling_request"
    name_scaling_response_queue = "dynamite_scaling_response"

    rabbit_mq_endpoint = "127.0.0.1:5672"
    rabbit_mq_endpoint_host = None
    rabbit_mq_endpoint_port = None

    etcd_endpoint = "127.0.0.1:4001"

    dynamite_executor_parameters = None
    rabbit_mq_connection = None

    def _create_rabbit_mq_connection(self):
        rabbit_mq_host = self.rabbit_mq_endpoint_host
        rabbit_mq_port = self.rabbit_mq_endpoint_port

        rabbit_mq_connection_parameters = pika.ConnectionParameters(host=rabbit_mq_host,
                                                                    port=rabbit_mq_port)

        self.rabbit_mq_connection = pika.BlockingConnection(rabbit_mq_connection_parameters)


    def scaling_request_received(self, ch, method, properties, body):
        # TODO: get the request and do some cool stuff (ok, just scale up or down)
        received_scaling_request_string = body.decode("utf-8")

        scaling_request = DynamiteScalingRequest(received_scaling_request_string)

        if scaling_request.command == DynamiteScalingCommand.SCALE_UP:
            service_name = scaling_request.service_name
            # self.dynamite_service_handler.add_new_fleet_service_instance(service_name)
        elif scaling_request.command == DynamiteScalingCommand.SCALE_DOWN:
            service_instance_name = scaling_request.service_instance_name
            # TODO implement functionality to remove specific fleet service instance
            #self.dynamite_service_handler.remove_fleet_service_instance(service_instance_name)

        # TODO: send the response (failure/success) to the response queue

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def _create_dynamite_config(self, etcd_endpoint):
        self.dynamite_config = DynamiteConfig(etcd_endpoint=etcd_endpoint)

    def _create_dynamite_service_handler(self, dynamite_config, etcd_endpoint):
        self.dynamite_service_handler = DynamiteServiceHandler(dynamite_config=dynamite_config,
                                                               etcd_endpoint=etcd_endpoint)

    def run(self):
        self._create_dynamite_config(self.etcd_endpoint)
        self._create_dynamite_service_handler(self.dynamite_config, self.etcd_endpoint)

        self._create_rabbit_mq_connection()

        channel = self.rabbit_mq_connection.channel()

        channel.basic_consume(self.scaling_request_received,
                              queue=self.name_scaling_request_queue,
                              no_ack=False)

        channel.start_consuming()
        scaling_request = {}


          # "command": "scale_up / scale_down",
          # "service": "service_name (e.g. zurmo_apache)",
          # "service_instance_name" : "service_instance_name (e.g. zurmo_apache@8080.service)"  --> will only be set when scaling down, otherwise set to 'None'
          # "failure_counter" : <int> --> starts at 0 and is increased when a failure occurs

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

        #self._create_rabbit_mq_connection()

#
# def create_connection(self):
#         self.connection = pika.BlockingConnection()
#
#     def message_received(self, ch, method, properties, body):
#         print(" [x] Received " + body.decode("utf-8"))
#         time.sleep(1)
#
#
#     def run(self):
#         self.create_connection()
#         channel = self.connection.channel()
#         channel.basic_consume(self.message_received,
#                       queue='hello',
#                       no_ack=True)
#
#         channel.start_consuming()


class DynamiteScalingCommand(object):
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"


class DynamiteScalingRequest(object):
    scaling_request_string = None

    command = None
    service_name = None
    service_instance_name = None
    failure_counter = None

    def __init__(self, scaling_request_string):
        if isinstance(scaling_request_string, str):
            self.scaling_request_string = scaling_request_string
        else:
            raise IllegalArgumentError("Error: argument <scaling_request_string> needs to be of type <str>")

        scaling_request_json = json.loads(self.scaling_request_string)

        self.command = scaling_request_json["command"]
        self.service_name = scaling_request_json["service_name"]
        self.service_instance_name = scaling_request_json["service_instance_name"]
        self.failure_counter = scaling_request_json["failure_counter"]


class DynamiteScalingResponse(object):

    command = None
    service_name = None
    service_instance_name = None
    failure_counter = None
    success = None

    def __init__(self, dynamite_scaling_request, success):

        if not isinstance(success, bool):
            raise IllegalArgumentError("Error: argument <success> needs to be of type <bool>")

        if isinstance(dynamite_scaling_request, DynamiteScalingRequest) and dynamite_scaling_request is not None:
            self.success = success
            self.command = dynamite_scaling_request.command
            self.service_name = dynamite_scaling_request.service_name
            self.service_instance_name = dynamite_scaling_request.service_instance_name
            self.failure_counter = dynamite_scaling_request.failure_counter

        else:
            raise IllegalArgumentError("Error: argument <scaling_request_string> needs to be of type <str>")

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
