__author__ = 'bloe'

class ScalingState:
    def update_and_report_if_action_required(self, policy, predicate_satisfied, timestamp, instance_uuid):
        pass

class ScalingStateTriggered(ScalingState):
    def update_and_report_if_action_required(self, policy, predicate_satisfied, timestamp, instance_uuid):
        threshold_period = policy.get_threshold_period_of_instance(instance_uuid)
        if threshold_period.is_in_period(timestamp):
            self._handle_in_period_case(predicate_satisfied, threshold_period, policy)
            return False
        else:
            self._handle_out_of_period_case(threshold_period, policy)
            return True

    @staticmethod
    def _handle_in_period_case(predicate_satisfied, threshold_period, policy):
        if not predicate_satisfied:
            ScalingStateTriggered._change_state_to_untriggered(threshold_period, policy)

    @staticmethod
    def _handle_out_of_period_case(threshold_period, policy):
        ScalingStateTriggered._change_state_to_untriggered(threshold_period, policy)

    @staticmethod
    def _change_state_to_untriggered(threshold_period, policy):
        threshold_period.reset()
        policy.state = ScalingStateUntriggered()

class ScalingStateUntriggered(ScalingState):
    def update_and_report_if_action_required(self, policy, predicate_satisfied, timestamp, instance_uuid):
        threshold_period = policy.get_threshold_period_of_instance(instance_uuid)
        if predicate_satisfied:
            threshold_period.start_period(timestamp)
            policy.state = ScalingStateTriggered()
        else:
            threshold_period.reset()
        return False


