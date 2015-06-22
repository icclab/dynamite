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


