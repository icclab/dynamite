__author__ = 'bloe'

import logging

class ScalingState:
    def update_and_report_if_action_required(self, policy, predicate_satisfied, timestamp, instance_uuid):
        pass

class ScalingStateTriggered(ScalingState):
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def update_and_report_if_action_required(self, policy, predicate_satisfied, timestamp, instance_uuid):
        threshold_period = policy.get_threshold_period_of_instance(instance_uuid)
        if threshold_period.is_in_period(timestamp):
            self._handle_in_period_case(predicate_satisfied, threshold_period, policy)
            return False
        else:
            self._handle_out_of_period_case(threshold_period, policy)
            return True

    def _handle_in_period_case(self, predicate_satisfied, threshold_period, policy):
        if not predicate_satisfied:
            self._logger.info("Change state to untriggered of policy %s because value not over/under threshold", str(policy))
            ScalingStateTriggered._change_state_to_untriggered(threshold_period, policy)

    def _handle_out_of_period_case(self, threshold_period, policy):
        ScalingStateTriggered._change_state_to_untriggered(threshold_period, policy)
        self._logger.info("Change state to untriggered of policy %s because threshold period is up", str(policy))

    @staticmethod
    def _change_state_to_untriggered(threshold_period, policy):
        threshold_period.reset()
        policy.state = ScalingStateUntriggered()

    def __repr__(self):
        return "ScalingStateTriggered"

class ScalingStateUntriggered(ScalingState):
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def update_and_report_if_action_required(self, policy, predicate_satisfied, timestamp, instance_uuid):
        threshold_period = policy.get_threshold_period_of_instance(instance_uuid)

        if predicate_satisfied:
            threshold_period.start_period(timestamp)
            self._logger.info("Change state to triggered of policy %s and instance %s", str(policy), instance_uuid)
            policy.state = ScalingStateTriggered()
        else:
            self._logger.info("Reset threshold period of instance %s of policy %s", instance_uuid, str(policy))
            threshold_period.reset()
        return False

    def __repr__(self):
        return "ScalingStateUntriggered"
