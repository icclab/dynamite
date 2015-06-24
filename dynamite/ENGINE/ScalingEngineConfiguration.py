__author__ = 'bloe'

class ScalingEngineConfiguration(object):
    def __init__(self):
        pass

    services_dictionary = {}
    metrics_receiver = None
    scaling_policies = []
    etcd_connection = None
    rabbit_mq_endpoint = None
    scaling_request_queue_name = None
    scaling_response_queue_name = None

    def __str__(self):
        return "ScalingEngineConfiguration(" \
               "services_dictionary={}," \
               "metrics_receiver={}," \
               "scaling_policies={}," \
               "etcd_connection={}," \
               "rabbit_mq_endpoint={}," \
               "scaling_request_queue_name={}," \
               "scaling_response_queue_name={}" \
               .format(
                    self.services_dictionary,
                    self.metrics_receiver,
                    self.scaling_policies,
                    self.etcd_connection,
                    self.rabbit_mq_endpoint,
                    self.scaling_request_queue_name,
                    self.scaling_response_queue_name
               )


