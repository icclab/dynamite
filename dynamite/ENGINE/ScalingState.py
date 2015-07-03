__author__ = 'bloe'

import logging

class ScalingState:

    def update_and_report_if_action_required(self, policy, predicate_satisfied, timestamp, instance_uuid):
        pass

class ScalingStateTriggered(ScalingState):
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def update_and_report_if_action_required(self, policy_instance, predicate_satisfied, timestamp, instance_uuid):
        threshold_period = policy_instance.threshold_period
        if threshold_period.is_in_period(timestamp):
            if not predicate_satisfied:
                self._logger.info("Change state to untriggered of policy %s because value not over/under threshold", str(policy_instance))
                self._change_state_to_untriggered(threshold_period, policy_instance)
            return False
        else:
            self._change_state_to_untriggered(threshold_period, policy_instance)
            self._logger.info("Change state to untriggered of policy %s because threshold period is up", str(policy_instance))
            return True

    def _change_state_to_untriggered(self, threshold_period, policy):
        threshold_period.reset()
        policy.state = ScalingStateUntriggered()

    def __repr__(self):
        return "ScalingStateTriggered"

class ScalingStateUntriggered(ScalingState):
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def update_and_report_if_action_required(self, policy_instance, predicate_satisfied, timestamp, instance_uuid):
        threshold_period = policy_instance.threshold_period

        if predicate_satisfied:
            threshold_period.start_period(timestamp)
            self._logger.info("Change state to triggered of policy instance %s", str(policy_instance))
            policy_instance.state = ScalingStateTriggered()
        else:
            self._logger.info("Reset threshold period of instance %s of policy %s", instance_uuid, str(policy_instance))
            threshold_period.reset()
        return False

    def __repr__(self):
        return "ScalingStateUntriggered"
