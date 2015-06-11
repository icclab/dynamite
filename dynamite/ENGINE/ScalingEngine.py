__author__ = 'bloe'

from dynamite.ENGINE.MetricsReceiver import MetricsReceiver
from dynamite.ENGINE.ScalingMetrics import ScalingMetrics
from dynamite.ENGINE.RuleChecker import RuleChecker
from dynamite.ENGINE.ExecutedTasksReceiver import ExecutedTaskReceiver
from dynamite.ENGINE.ScalingActionSender import ScalingActionSender
from dynamite.ENGINE.RunningServicesRegistry import RunningServicesRegistry

class ScalingEngine(object):
    def __init__(self):
        self._metrics_receiver = MetricsReceiver()
        self._metrics = ScalingMetrics()
        self._rule_checker = RuleChecker()
        self._executed_tasks_receiver = ExecutedTaskReceiver()
        self._scaling_action_sender = ScalingActionSender()
        self._running_services_registry = RunningServicesRegistry()

    def start(self):
        while True:
            # get metrics from etcd queue
            metrics_message = self._metrics_receiver.receive_metrics()

            # aggregate metrics per type
            self._metrics.add_metrics(metrics_message)

            # check if scaleup/scaledown policy applies
            scaling_actions = self._rule_checker.check(self._metrics)

            # convert uuid to service name
            service_name = self._convert_uuid_to_service_name()

            for scaling_action in scaling_actions:
                # write action to rabbitmq queue if needed
                self._scaling_action_sender.send_action(scaling_action)

            # check if responses available from executor
            executed_tasks = self._executed_tasks_receiver.receive()

            for executed_task in executed_tasks:
                # update service count: self._running_services_registry.add/remove
                pass

    def _convert_uuid_to_service_name(self, uuid):
        # TODO: implement converting of uuid to service name
        return ""

