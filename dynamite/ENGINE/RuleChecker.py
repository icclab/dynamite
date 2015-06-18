__author__ = 'bloe'

from dynamite.ENGINE.ScalingAction import ScalingAction
from dynamite.ENGINE.ScalingPolicy import ScalingPolicy

class RuleChecker(object):
    def __init__(self, scaling_policies, service_dictionary):
        self._scaling_policies_by_metric = {}
        self._scaling_policy_details_per_name = {}
        self._initialize_scaling_policies(scaling_policies, service_dictionary)

    def _initialize_scaling_policies(self, scaling_policy_configurations, service_dictionary):
        for scaling_policy_config in scaling_policy_configurations:
            if scaling_policy_config.name not in self._scaling_policy_details_per_name:
                self._scaling_policy_details_per_name[scaling_policy_config.name] = scaling_policy_config

        for service_name, service in service_dictionary.items():
            scale_down_policy_details = self._find_scaling_policy_details_by_name(
                service.service_config_details.scale_down_policy
            )
            scale_up_policy_details = self._find_scaling_policy_details_by_name(
                service.service_config_details.scale_up_policy
            )
            scale_down_policy = ScalingPolicy(scale_down_policy_details, service)
            self._add_scaling_policy_by_metric(scale_down_policy_details.metric, scale_down_policy)
            scale_up_policy = ScalingPolicy(scale_up_policy_details, service)
            self._add_scaling_policy_by_metric(scale_up_policy_details.metric, scale_up_policy)

    def _add_scaling_policy_by_metric(self, metric, policy):
        if not metric in self._scaling_policies_by_metric:
            self._scaling_policies_by_metric[metric] = []
        self._scaling_policies_by_metric[metric].append(policy)

    def _find_scaling_policy_details_by_name(self, name):
        return self._scaling_policy_details_per_name(name)

    def check_and_return_needed_scaling_actions(self, metric_message):
        related_policies = self._scaling_policies_by_metric[metric_message.metric_name]
        scaling_actions = []
        for policy in related_policies:
            scaling_actions.extend(policy.update_policy_state_and_get_scaling_actions(metric_message))
        return scaling_actions

