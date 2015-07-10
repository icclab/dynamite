__author__ = 'bloe'

class ScalingEngineConfiguration(object):
    def __init__(self):
        pass

    services_dictionary = {}
    metrics_receiver = None
    scaling_policies = []
    etcd_connection = None
    executed_task_receiver = None
    scaling_action_sender = None

    def __repr__(self):
        return "ScalingEngineConfiguration(" \
               "services_dictionary={}," \
               "metrics_receiver={}," \
               "scaling_policies={}," \
               "etcd_connection={}," \
               "executed_task_receiver={}," \
               "scaling_action_sender={}" \
               .format(
                    self.services_dictionary,
                    self.metrics_receiver,
                    self.scaling_policies,
                    self.etcd_connection,
                    self.executed_task_receiver,
                    self.scaling_action_sender
               )


