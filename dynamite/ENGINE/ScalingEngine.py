__author__ = 'bloe'

import atexit

from dynamite.ENGINE.ScalingMetrics import ScalingMetrics
from dynamite.ENGINE.RuleChecker import RuleChecker
from dynamite.ENGINE.ExecutedTasksReceiver import ExecutedTaskReceiver
from dynamite.ENGINE.ScalingActionSender import ScalingActionSender
from dynamite.ENGINE.RunningServicesRegistry import RunningServicesRegistry
from dynamite.ENGINE.ServiceInstanceNameResolver import CachingServiceInstanceNameResolver, ServiceInstanceNameResolver
from dynamite.EXECUTOR.DynamiteScalingRequest import DynamiteScalingRequest
from dynamite.EXECUTOR.DynamiteScalingCommand import DynamiteScalingCommand

class ScalingEngine(object):
    AGGREGATE_METRICS = False
    RETRANSMIT_COUNT_OF_FAILED_MESSAGES = 5

    def __init__(self, configuration):
        self._services_dictionary = configuration.services_dictionary
        self._metrics_receiver = configuration.metrics_receiver
        self._metrics = ScalingMetrics()
        self._rule_checker = RuleChecker(configuration.scaling_policies, configuration.services_dictionary)
        self._executed_tasks_receiver = ExecutedTaskReceiver(
            configuration.rabbit_mq_endpoint,
            configuration.scaling_response_queue_name
        )
        self._scaling_action_sender = ScalingActionSender(
            configuration.rabbit_mq_endpoint,
            configuration.scaling_request_queue_name
        )
        atexit.register(self._on_engine_shutdown)
        self._running_services_registry = RunningServicesRegistry(configuration.services_dictionary)
        instance_name_resolver = ServiceInstanceNameResolver(configuration.etcd_connection)
        self._service_instance_name_resolver = CachingServiceInstanceNameResolver(instance_name_resolver)

    def start(self):
        self._start_minimal_required_services()

        while True:
            try:
                metrics_message = self._retreive_metrics()
                scaling_actions = self._rule_checker.check_and_return_needed_scaling_actions(metrics_message)
                self._send_filtered_scaling_actions(scaling_actions)
                executed_tasks = self._executed_tasks_receiver.receive()
                self._update_running_tasks_registry(executed_tasks)
                self._resend_failed_messages(executed_tasks)
            except Exception:
                # TODO: log exception
                pass

    def _retreive_metrics(self):
        # get metrics from etcd queue
        metrics_message = self._metrics_receiver.receive_metrics()

        if self.AGGREGATE_METRICS:
            # aggregate metrics per type
            self._metrics.add_metrics(metrics_message)
        return metrics_message

    def _send_filtered_scaling_actions(self, scaling_actions):
        for scaling_action in scaling_actions:
            if self._running_services_registry.scaling_action_allowed(scaling_action):
                if scaling_action.command == DynamiteScalingCommand.SCALE_DOWN:
                    scaling_action.service_instance_name = self._service_instance_name_resolver.resolve(
                        scaling_action.uuid
                    )
                self._scaling_action_sender.send_action(DynamiteScalingRequest.from_scaling_action(scaling_action))
            else:
                continue

    def _update_running_tasks_registry(self, executed_tasks):
        for executed_task in executed_tasks:
            if executed_task.success:
                self._add_remove_running_service_based_on_command(executed_task)

    def _add_remove_running_service_based_on_command(self, executor_response):
        if executor_response.command == DynamiteScalingCommand.SCALE_UP:
            self._running_services_registry.add_running_service(executor_response.service_name)
        elif executor_response.command == DynamiteScalingCommand.SCALE_DOWN:
            self._running_services_registry.remove_running_service(executor_response.service_name)
        else:
            raise ValueError("Unknown command {}, cannot parse executor response: {}".format(
                executor_response.command,
                executor_response)
            )

    def _resend_failed_messages(self, executor_response_messages):
        for executor_response in executor_response_messages:
            if executor_response.success:
                continue
            if executor_response.failure_counter <= self.RETRANSMIT_COUNT_OF_FAILED_MESSAGES:
                executor_response.failure_counter += 1
                self._scaling_action_sender.send_action(executor_response)
            else:
                self._report_failed_scaling_message(executor_response)

    def _report_failed_scaling_message(self, executor_response):
        # TODO: log failed scaling message
        pass

    def _on_engine_shutdown(self):
        self._scaling_action_sender.close()
        self._executed_tasks_receiver.close()

    def _start_minimal_required_services(self):
        for service_name, service in self._services_dictionary.items():
            running_services = self._running_services_registry.number_of_running_instances_of_service(service_name)
            if service.service_config_details.min_instance is None:
                continue
            services_to_start = service.service_config_details.min_instance - running_services
            services_to_start = 0 if services_to_start < 0 else services_to_start
            for x in range(0, services_to_start):
                request = DynamiteScalingRequest.from_service(service, DynamiteScalingCommand.SCALE_UP)
                self._scaling_action_sender.send_action(request)
