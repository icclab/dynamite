__author__ = 'bloe'

import logging
import dateutil.parser
from dynamite.ENGINE.ScalingState import ScalingStateUntriggered
from dynamite.ENGINE.TimePeriod import TimePeriod

class ScalingPolicyInstance:

    _latest_metric_update = None

    state = None
    policy = None
    instance_uuid = None
    threshold_period = None

    def __init__(self, instance_uuid, policy):
        self._logger = logging.getLogger(__name__)
        self.state = ScalingStateUntriggered()
        threshold_period_in_seconds = policy.get_threshold_period_in_seconds()
        self._logger.debug("threshold period of policy %s is %d", policy, threshold_period_in_seconds)
        self.threshold_period = TimePeriod(threshold_period_in_seconds)
        self._latest_metric_update = None
        self.instance_uuid = instance_uuid
        self.policy = policy

    def update_policy_state_and_get_scaling_actions(self, metrics_message):
        scaling_actions = []

        for metric_value in metrics_message.metric_values:
            value = metric_value.value
            timestamp = dateutil.parser.parse(metric_value.timestamp)

            if not self._is_new_metric(timestamp):
                self._logger.debug("metric value %s is outdated for instance %s", repr(metric_value), self.instance_uuid)
                continue

            if self.policy.cooldown_period.is_in_period(timestamp):
                self._logger.debug("metric value %s ignored because of cooldown is active", repr(metric_value))
                continue

            predicate_satisfied = self.policy.value_exceeds_or_undercuts_threshold(float(value))
            self._logger.debug("metric value %s is %s under/over threshold",
                               repr(metric_value),
                               "" if predicate_satisfied else "not"
                               )

            cooldown_start_time = timestamp
            if self.threshold_period.period_started:
                cooldown_start_time = self.threshold_period.calculate_period_end()

            action_required = self.state.update_and_report_if_action_required(
                self,
                predicate_satisfied,
                timestamp,
                metrics_message.uuid
            )

            if action_required:
                scaling_action = self.policy.create_scaling_action(metrics_message.metric_name, self.instance_uuid)
                self.policy.cooldown_period.start_period(cooldown_start_time)
                scaling_actions.append(scaling_action)
                self._logger.info("Triggered scaling action %s, beginning cooldown", repr(scaling_action))

        return scaling_actions

    def _is_new_metric(self, timestamp):
        if self._latest_metric_update is None:
            self._latest_metric_update = timestamp
            return True

        new_metric = timestamp > self._latest_metric_update
        if new_metric:
            self._latest_metric_update = timestamp
        return new_metric

    def __repr__(self):
        return "ScalingPolicyInstance(instance_uuid={},state={},threshold_period={},policy={})".format(
            self.instance_uuid,
            repr(self.state),
            repr(self.threshold_period),
            repr(self.policy)
        )
