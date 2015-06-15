__author__ = 'brnr'
import pika
import json
import time

def create_rabbit_mq_connection():
    rabbit_mq_host = '127.0.0.1'
    rabbit_mq_port = 5672

    rabbit_mq_connection_parameters = pika.ConnectionParameters(host=rabbit_mq_host,
                                                                port=rabbit_mq_port)

    rabbit_mq_connection = pika.BlockingConnection(rabbit_mq_connection_parameters)

    return rabbit_mq_connection


def create_scaling_request_string():

    scaling_request = {
        "command": "scale_up",
        "service_name": "a",
        "service_instance_name": None,
        "failure_counter": 0
    }

    scaling_request_string = json.dumps(scaling_request)

    return scaling_request_string

if __name__ == '__main__':
    dynamite_scaling_request = "dynamite_scaling_request"
    dynamite_scaling_response = "dynamite_scaling_response"

    connection = create_rabbit_mq_connection()

    channel = connection.channel()
    channel.queue_declare(queue="dynamite_scaling_request", durable=True)
    channel.queue_declare(queue="dynamite_scaling_response", durable=True)

    for i in range(10):
        scaling_request = create_scaling_request_string()

        channel.basic_publish(exchange='',
                              routing_key=dynamite_scaling_request,
                              body=scaling_request)

    connection.close()