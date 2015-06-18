__author__ = 'bloe'

from dynamite.ENGINE.ScalingMetrics import ScalingMetrics
from dynamite.ENGINE.RuleChecker import RuleChecker
from dynamite.ENGINE.ExecutedTasksReceiver import ExecutedTaskReceiver
from dynamite.ENGINE.ScalingActionSender import ScalingActionSender
from dynamite.ENGINE.RunningServicesRegistry import RunningServicesRegistry
from dynamite.ENGINE.ServiceInstanceNameResolver import ServiceInstanceNameResolver

class ScalingEngine(object):
    def __init__(self, configuration):
        self._metrics_receiver = configuration.metrics_receiver
        self._metrics = ScalingMetrics()
        self._rule_checker = RuleChecker(configuration.scaling_policies, configuration.services_dictionary)
        self._executed_tasks_receiver = ExecutedTaskReceiver()
        self._scaling_action_sender = ScalingActionSender()
        self._running_services_registry = RunningServicesRegistry()
        self._services_dictionary = configuration.services_dictionary
        self._aggregate_metrics = False
        self._service_instance_name_resolver = ServiceInstanceNameResolver()

    def start(self):
        self._running_services_registry.initialize_from_service_dictionary(self._services_dictionary)

        while True:
            # get metrics from etcd queue
            metrics_message = self._metrics_receiver.receive_metrics()

            if self._aggregate_metrics:
                # aggregate metrics per type
                self._metrics.add_metrics(metrics_message)

            # check if scaleup/scaledown policy applies
            scaling_actions = self._rule_checker.check_and_return_needed_scaling_actions(metrics_message)

            for scaling_action in scaling_actions:
                # convert uuid to service name
                scaling_action.service_instance_name = self._service_instance_name_resolver.resolve(scaling_action.uuid)

            for scaling_action in scaling_actions:
                # check if scaling_action really should be sent to executor (min/max instances)

                # write action to rabbitmq queue if needed
                self._scaling_action_sender.send_action(scaling_action)

            # check if responses available from executor
            executed_tasks = self._executed_tasks_receiver.receive()

            for executed_task in executed_tasks:
                # update service count: self._running_services_registry.add/remove
                pass

