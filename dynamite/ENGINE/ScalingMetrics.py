__author__ = 'bloe'


class ScalingMetrics:
    def __init__(self):
        self._metrics_of_service = {}

    def add_metrics(self, metrics_message):
        self._metrics_of_service[metrics_message.service_name] += set(metrics_message.metrics_values)

    def cleanup_old_metrics(self, older_than_seconds):
        # TODO: implement delete of old metrics
        pass