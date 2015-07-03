__author__ = 'bloe'

import logging
import dateutil.parser
from enum import Enum
from dynamite.ENGINE.TimePeriod import TimePeriod
from dynamite.ENGINE.ScalingState import ScalingStateUntriggered
from dynamite.ENGINE.ScalingAction import ScalingAction
from dynamite.EXECUTOR.DynamiteEXECUTOR import DynamiteScalingCommand
from dynamite.ENGINE.ScalingPolicyInstance import ScalingPolicyInstance

class ScalingPolicyType(Enum):
    scale_up = 1
    scale_down = 2

class ScalingPolicy(object):
    MINUTES_IN_HOUR = 60
    SECONDS_IN_MINUTE = 60

    _policy_instances = None

    cooldown_period = None
    state = None
    service = None
    policy_name = None
    service_type = None

    def __init__(self, scaling_policy_configuration, service, scaling_policy_type):
        self._logger = logging.getLogger(__name__)
        self._policy_instances = {}
        self.state = ScalingStateUntriggered()
        self._policy_config = scaling_policy_configuration
        self.service_type = self._policy_config.service_type
        self.policy_name = scaling_policy_configuration.name
        cooldown_period_in_seconds = self._calculate_period_in_seconds(
            scaling_policy_configuration.cooldown_period,
            scaling_policy_configuration.cooldown_period_unit
        )
        self._logger.debug("cooldown period of policy %s is %d", self.policy_name, cooldown_period_in_seconds)
        self.cooldown_period = TimePeriod(cooldown_period_in_seconds)
        self.service = service
        self._last_in_period_uuid_of_service_type = {}
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
        policy_instance = self._get_or_create_policy_instance(metrics_message.uuid)
        return policy_instance.update_policy_state_and_get_scaling_actions(metrics_message)

    def _get_or_create_policy_instance(self, instance_uuid):
        if instance_uuid not in self._policy_instances:
            policy_instance = ScalingPolicyInstance(instance_uuid, self)
            self._policy_instances[instance_uuid] = policy_instance
        return self._policy_instances[instance_uuid]

    def create_scaling_action(self, metric_name, instance_uuid):
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

    def get_last_in_period_uuid_of_service_type(self, service_type):
        if not service_type in self._last_in_period_uuid_of_service_type:
            return None
        return self._last_in_period_uuid_of_service_type[service_type]

    def set_last_in_period_uuid_of_service_type(self, service_type, uuid):
        self._last_in_period_uuid_of_service_type[service_type] = uuid

    def value_exceeds_or_undercuts_threshold(self, value):
        predicate_method = self._get_policy_predicate_operation()
        return predicate_method(
            float(value),
            self._policy_config.threshold
        )

    def _get_policy_predicate_operation(self):
        operation_string = self._policy_config.comparative_operator
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

    def get_threshold_period_in_seconds(self):
        return self._calculate_period_in_seconds(
            self._policy_config.period,
            self._policy_config.period_unit
        )

    def __repr__(self):
        return "ScalingPolicy(policy_name={},cooldown_period={},state={},service={})".format(
            self.policy_name,
            repr(self.cooldown_period),
            repr(self.state),
            repr(self.service)
        )
