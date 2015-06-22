__author__ = 'bloe'

from dynamite.ENGINE.ScalingMetrics import ScalingMetrics
from dynamite.ENGINE.RuleChecker import RuleChecker
from dynamite.ENGINE.ExecutedTasksReceiver import ExecutedTaskReceiver
from dynamite.ENGINE.ScalingActionSender import ScalingActionSender
from dynamite.ENGINE.RunningServicesRegistry import RunningServicesRegistry
from dynamite.ENGINE.ServiceInstanceNameResolver import CachingServiceInstanceNameResolver
from dynamite.EXECUTOR.DynamiteScalingRequest import DynamiteScalingRequest

class ScalingEngine(object):
    AGGREGATE_METRICS = False

    def __init__(self, configuration):
        self._metrics_receiver = configuration.metrics_receiver
        self._metrics = ScalingMetrics()
        self._rule_checker = RuleChecker(configuration.scaling_policies, configuration.services_dictionary)
        self._executed_tasks_receiver = ExecutedTaskReceiver()
        self._scaling_action_sender = ScalingActionSender()
        self._running_services_registry = RunningServicesRegistry(configuration.services_dictionary)
        self._service_instance_name_resolver = CachingServiceInstanceNameResolver()

    def start(self):
        # TODO: start minimal service count

        while True:
            # get metrics from etcd queue
            metrics_message = self._metrics_receiver.receive_metrics()

            if self.AGGREGATE_METRICS:
                # aggregate metrics per type
                self._metrics.add_metrics(metrics_message)

            # check if scaleup/scaledown policy applies
            scaling_actions = self._rule_checker.check_and_return_needed_scaling_actions(metrics_message)

            for scaling_action in scaling_actions:
                if self._running_services_registry.scaling_action_allowed(scaling_action):
                    scaling_action.service_instance_name = self._service_instance_name_resolver.resolve(
                        scaling_action.uuid
                    )

                    # TODO: write action to rabbitmq queue if needed
                    self._scaling_action_sender.send_action(DynamiteScalingRequest.from_scaling_action(scaling_action))
                else:
                    continue

            # TODO: check if responses available from executor
            executed_tasks = self._executed_tasks_receiver.receive()

            for executed_task in executed_tasks:
                # TODO: update service count: self._running_services_registry.add/remove
                pass
