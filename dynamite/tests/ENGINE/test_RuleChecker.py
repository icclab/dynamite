__author__ = 'bloe'

from dynamite.ENGINE.RuleChecker import RuleChecker
from dynamite.ENGINE.MetricsMessage import MetricsMessage
from dynamite.ENGINE.MetricValue import MetricValue
from dynamite.INIT.DynamiteConfig import DynamiteConfig
from dynamite.GENERAL.FleetService import FleetService
from dynamite.EXECUTOR.DynamiteScalingCommand import DynamiteScalingCommand

class TestRuleChecker:

    message_scaledown_noaction = MetricsMessage(
        "apache",
        "apache-uuid",
        [
            # no scaling because > 30 for 60s
            MetricValue("2015-06-18T07:56:14.632Z", "30.1"),
            MetricValue("2015-06-18T07:56:15.632Z", "30.2"),
            MetricValue("2015-06-18T07:56:16.632Z", "30.2"),
            MetricValue("2015-06-18T07:56:17.632Z", "30.2"),
            MetricValue("2015-06-18T07:56:20.632Z", "30.15"),
            MetricValue("2015-06-18T07:56:25.632Z", "30.3"),
            MetricValue("2015-06-18T07:56:50.632Z", "30.25"),
            MetricValue("2015-06-18T07:57:15.632Z", "30.7"),
            MetricValue("2015-06-18T07:57:25.632Z", "30.8"),
            MetricValue("2015-06-18T07:57:35.632Z", "30.9"),
            MetricValue("2015-06-18T07:57:45.632Z", "31.0"),
        ],
        "cpu_utilization"
    )
    message_scaledown_action = MetricsMessage(
        "apache",
        "apache-uuid",
        [
            # scaling should happen here (< 30 for 60s)
            MetricValue("2015-06-18T07:58:14.632Z", "29.1"),
            MetricValue("2015-06-18T07:58:15.632Z", "29.9"),
            MetricValue("2015-06-18T07:58:16.632Z", "29.9999999"),
            MetricValue("2015-06-18T07:58:17.632Z", "01.2"),
            MetricValue("2015-06-18T07:58:20.632Z", "0.15"),
            MetricValue("2015-06-18T07:58:25.632Z", "0.3"),
            MetricValue("2015-06-18T07:58:50.632Z", "20.25"),
            MetricValue("2015-06-18T07:59:15.632Z", "25.7"),
            MetricValue("2015-06-18T07:59:25.632Z", "28.8"),
            MetricValue("2015-06-18T07:59:35.632Z", "29.9"),
            MetricValue("2015-06-18T07:59:45.632Z", "10.0"),
        ],
        "cpu_utilization"
    )
    message_scaledown_cooldown = MetricsMessage(
        "apache",
        "apache-uuid",
        [
            # no scaling because cooldown
            MetricValue("2015-06-18T08:00:14.632Z", "3.1"),
            MetricValue("2015-06-18T08:00:15.632Z", "3.2"),
            MetricValue("2015-06-18T08:00:16.632Z", "3.2"),
            MetricValue("2015-06-18T08:00:17.632Z", "3.2"),
            MetricValue("2015-06-18T08:00:20.632Z", "3.15"),
            MetricValue("2015-06-18T08:00:25.632Z", "3.3"),
            MetricValue("2015-06-18T08:00:50.632Z", "3.25"),
            MetricValue("2015-06-18T08:01:15.632Z", "1.7"),
            MetricValue("2015-06-18T08:01:25.632Z", "1.8"),
            MetricValue("2015-06-18T08:01:35.632Z", "1.9"),
            MetricValue("2015-06-18T08:01:45.632Z", "1.0"),
        ],
        "cpu_utilization"
    )
    message_scaledown_noaction2 = MetricsMessage(
        "apache",
        "apache-uuid",
        [
            # no scaling because threshold period
            MetricValue("2015-06-18T08:01:14.632Z", "29.1"),
            MetricValue("2015-06-18T08:01:15.632Z", "29.2"),
            MetricValue("2015-06-18T08:01:16.632Z", "30.1"),
            MetricValue("2015-06-18T08:01:17.632Z", "29.2"),
            MetricValue("2015-06-18T08:01:20.632Z", "29.15"),
            MetricValue("2015-06-18T08:01:25.632Z", "28.3"),
            MetricValue("2015-06-18T08:01:50.632Z", "29.25"),
            MetricValue("2015-06-18T08:02:15.632Z", "28.7"),
            MetricValue("2015-06-18T08:02:25.632Z", "30.8"),
            MetricValue("2015-06-18T08:02:35.632Z", "29.9"),
            MetricValue("2015-06-18T08:02:45.632Z", "29.0"),
        ],
        "cpu_utilization"
    )

    message_scaleup_noaction = MetricsMessage(
        "apache",
        "apache-uuid",
        [
            # no scaling should happen here
            MetricValue("2015-06-18T07:56:14.632Z", "100.1"),
            MetricValue("2015-06-18T07:56:15.632Z", "100.2"),
            MetricValue("2015-06-18T07:56:16.632Z", "100.2"),
            MetricValue("2015-06-18T07:56:17.632Z", "100.2"),
            MetricValue("2015-06-18T07:56:20.632Z", "100.15"),
            MetricValue("2015-06-18T07:56:25.632Z", "100.3"),
            MetricValue("2015-06-18T07:56:50.632Z", "100.25"),
            MetricValue("2015-06-18T07:57:15.632Z", "100.7"),
            MetricValue("2015-06-18T07:57:25.632Z", "100.8"),
            MetricValue("2015-06-18T07:57:35.632Z", "100.9"),
            MetricValue("2015-06-18T07:57:45.632Z", "101.0"),
        ],
        "response_time"
    )
    message_scaleup_action = MetricsMessage(
        "apache",
        "apache-uuid",
        [
            # scaling because > 500 for 60s
            MetricValue("2015-06-18T07:58:14.632Z", "500.1"),
            MetricValue("2015-06-18T07:58:15.632Z", "500.2"),
            MetricValue("2015-06-18T07:58:16.632Z", "500.2"),
            MetricValue("2015-06-18T07:58:17.632Z", "500.2"),
            MetricValue("2015-06-18T07:58:20.632Z", "500.15"),
            MetricValue("2015-06-18T07:58:25.632Z", "500.3"),
            MetricValue("2015-06-18T07:58:50.632Z", "500.25"),
            MetricValue("2015-06-18T07:59:15.632Z", "500.7"),
            MetricValue("2015-06-18T07:59:25.632Z", "500.8"),
            MetricValue("2015-06-18T07:59:35.632Z", "500.9"),
            MetricValue("2015-06-18T07:59:45.632Z", "501.0"),
        ],
        "response_time"
    )
    message_scaleup_cooldown = MetricsMessage(
        "apache",
        "apache-uuid",
        [
            # no scaling because cooldown
            MetricValue("2015-06-18T08:00:14.632Z", "500.1"),
            MetricValue("2015-06-18T08:00:15.632Z", "500.2"),
            MetricValue("2015-06-18T08:00:16.632Z", "500.2"),
            MetricValue("2015-06-18T08:00:17.632Z", "500.2"),
            MetricValue("2015-06-18T08:00:20.632Z", "500.15"),
            MetricValue("2015-06-18T08:00:25.632Z", "500.3"),
            MetricValue("2015-06-18T08:00:50.632Z", "500.25"),
            MetricValue("2015-06-18T08:01:15.632Z", "500.7"),
            MetricValue("2015-06-18T08:01:25.632Z", "500.8"),
            MetricValue("2015-06-18T08:01:35.632Z", "500.9"),
            MetricValue("2015-06-18T08:01:45.632Z", "501.0"),
        ],
        "response_time"
    )
    message_scaleup_noaction2 = MetricsMessage(
        "apache",
        "apache-uuid",
        [
            # no scaling because threshold period
            MetricValue("2015-06-18T08:01:14.632Z", "500.1"),
            MetricValue("2015-06-18T08:01:15.632Z", "500.2"),
            MetricValue("2015-06-18T08:01:16.632Z", "300.2"),
            MetricValue("2015-06-18T08:01:17.632Z", "500.2"),
            MetricValue("2015-06-18T08:01:20.632Z", "500.15"),
            MetricValue("2015-06-18T08:01:25.632Z", "300.3"),
            MetricValue("2015-06-18T08:01:50.632Z", "700.25"),
            MetricValue("2015-06-18T08:02:15.632Z", "300.7"),
            MetricValue("2015-06-18T08:02:25.632Z", "800.8"),
            MetricValue("2015-06-18T08:02:35.632Z", "300.9"),
            MetricValue("2015-06-18T08:02:45.632Z", "910.0"),
        ],
        "response_time"
    )

    scale_up_policy_details = DynamiteConfig.ScalingPolicyStruct.ScalingPolicyDetailStruct(
        "scale_down",
        {
            "service": "apache",
            "metric": "cpu_utilization",
            "comparative_operator": "lt",
            "threshold": 30,
            "period": 60,
            "period_unit": "second",
            "cooldown_period": 120,
            "cooldown_period_unit": "second"
        }
    )

    scale_down_policy_details = DynamiteConfig.ScalingPolicyStruct.ScalingPolicyDetailStruct(
        "scale_up",
        {
            "service": "apache",
            "metric": "response_time",
            "comparative_operator": "gt",
            "threshold": 500,
            "period": 60,
            "period_unit": "second",
            "cooldown_period": 120,
            "cooldown_period_unit": "second"
        }
    )

    service = FleetService("apache")
    service.service_config_details = DynamiteConfig.ServiceStruct.ServiceDetailStruct("apache", {
        "scale_up_policy": {"ScalingPolicy": "scale_up"},
        "scale_down_policy": {"ScalingPolicy": "scale_down"}
    })

    service_dictionary = {
        "apache": service
    }

    scaling_policies = [
        scale_up_policy_details,
        scale_down_policy_details
    ]

    def test_check_and_return_needed_scaling_actions_with_scaledown_metrics(self):
        ruleChecker = RuleChecker(self.scaling_policies, self.service_dictionary)

        result = ruleChecker.check_and_return_needed_scaling_actions(self.message_scaledown_noaction)
        assert result == []

        result = ruleChecker.check_and_return_needed_scaling_actions(self.message_scaledown_action)
        assert result is not None and result != []
        assert len(result) == 1
        result = result[0]
        assert result.service_name == self.message_scaledown_noaction.service_name
        assert result.uuid == self.message_scaledown_noaction.uuid
        assert result.command == DynamiteScalingCommand.SCALE_DOWN

        result = ruleChecker.check_and_return_needed_scaling_actions(self.message_scaledown_cooldown)
        assert result == []

        result = ruleChecker.check_and_return_needed_scaling_actions(self.message_scaledown_noaction2)
        assert result == []

    def test_check_and_return_needed_scaling_actions_with_scaleup_metrics(self):
        ruleChecker = RuleChecker(self.scaling_policies, self.service_dictionary)

        result = ruleChecker.check_and_return_needed_scaling_actions(self.message_scaleup_noaction)
        assert result == []

        result = ruleChecker.check_and_return_needed_scaling_actions(self.message_scaleup_action)
        assert result is not None and result != []
        assert len(result) == 1
        result = result[0]
        assert result.service_name == self.message_scaleup_noaction.service_name
        assert result.uuid == self.message_scaleup_noaction.uuid
        assert result.command == DynamiteScalingCommand.SCALE_UP

        result = ruleChecker.check_and_return_needed_scaling_actions(self.message_scaleup_cooldown)
        assert result == []

        result = ruleChecker.check_and_return_needed_scaling_actions(self.message_scaleup_noaction2)
        assert result == []
