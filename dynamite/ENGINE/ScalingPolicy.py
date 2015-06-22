__author__ = 'bloe'

from dynamite.ENGINE.TimePeriod import TimePeriod
from dynamite.ENGINE.ScalingState import ScalingStateUntriggered
from dynamite.ENGINE.ScalingAction import ScalingAction
from dynamite.EXECUTOR.DynamiteEXECUTOR import DynamiteScalingCommand
import dateutil.parser
from enum import Enum

class ScalingPolicyType(Enum):
    scale_up = 1
    scale_down = 2

class ScalingPolicy(object):
    MINUTES_IN_HOUR = 60
    SECONDS_IN_MINUTE = 60

    cooldown_period = None
    state = None
    service = None
    policy_name = None

    def __init__(self, scaling_policy_configuration, service, scaling_policy_type):
        self.state = ScalingStateUntriggered()
        self._policy_config = scaling_policy_configuration
        self.policy_name = scaling_policy_configuration.name
        self._threshold_period_in_seconds = self._calculate_period_in_seconds(
            scaling_policy_configuration.period,
            scaling_policy_configuration.period_unit
        )
        cooldown_period_in_seconds = self._calculate_period_in_seconds(
            scaling_policy_configuration.cooldown_period,
            scaling_policy_configuration.cooldown_period_unit
        )
        self.cooldown_period = TimePeriod(cooldown_period_in_seconds)
        self._latest_metric_update_of_instance = {}
        self.service = service
        self._threshold_period_per_instance = {}
        self._scaling_policy_type = scaling_policy_type

    def _calculate_period_in_seconds(self, number, unit):
        conversion_methods = {
            "second": lambda x: x,
            "minute": self._minutes_to_seconds,
            "hour": self._hours_to_seconds
        }
        if not unit in conversion_methods:
            raise ValueError("Could not find unit {}. Allowed values are 'second', 'minute', 'hour'.".format(unit))
        return conversion_methods[unit](number)

    def _minutes_to_seconds(self, minutes):
        return minutes * self.SECONDS_IN_MINUTE

    def _hours_to_seconds(self, hours):
        return self._minutes_to_seconds(hours * self.MINUTES_IN_HOUR)

    def update_policy_state_and_get_scaling_actions(self, metrics_message):
        scaling_actions = []

        predicate_method = self._get_policy_predicate_operation(self._policy_config.comparative_operator)

        for metric_value in metrics_message.metric_values:
            for timestamp, value in metric_value.items():
                timestamp = dateutil.parser.parse(timestamp)

                if not self._is_new_metric(timestamp, metrics_message.uuid):
                    continue

                if self.cooldown_period.is_in_period(timestamp):
                    continue

                predicate_satisfied = predicate_method(
                    float(value),
                    self._policy_config.threshold
                )
                action_required = self.state.update_and_report_if_action_required(
                    self,
                    predicate_satisfied,
                    timestamp,
                    metrics_message.uuid
                )
                if action_required:
                    scaling_action = self._create_scaling_action(metrics_message.metric_name, metrics_message.uuid)
                    self.cooldown_period.start_period(timestamp)
                    scaling_actions.append(scaling_action)

        return scaling_actions

    @staticmethod
    def _get_policy_predicate_operation(operation_string):
        policy_predicate = {
            "lt": lambda x, limit: x < limit,
            "gt": lambda x, limit: x > limit
        }
        if not operation_string in policy_predicate:
            raise ValueError(
                "Could not find operator {}. Allowed values are 'lt', 'gt'.".format(
                    operation_string
                )
            )
        return policy_predicate[operation_string]

    def get_threshold_period_of_instance(self, instance_name):
        if instance_name not in self._threshold_period_per_instance:
            self._threshold_period_per_instance[instance_name] = TimePeriod(self._threshold_period_in_seconds)
        return self._threshold_period_per_instance[instance_name]

    def _is_new_metric(self, timestamp, instance):
        if not instance in self._latest_metric_update_of_instance:
            self._latest_metric_update_of_instance[instance] = timestamp
            return True
        new_metric = timestamp > self._latest_metric_update_of_instance[instance]
        if new_metric:
            self._latest_metric_update_of_instance[instance] = timestamp
        return new_metric

    def _create_scaling_action(self, metric_name, instance_uuid):
        scaling_action = ScalingAction(self.service.name)
        scaling_action.metric_name = metric_name
        scaling_action.command = self._find_out_scaling_command()
        scaling_action.uuid = instance_uuid
        return scaling_action

    def _find_out_scaling_command(self):
        if self._scaling_policy_type == ScalingPolicyType.scale_up:
            return DynamiteScalingCommand.SCALE_UP
        else:
            return DynamiteScalingCommand.SCALE_DOWN
