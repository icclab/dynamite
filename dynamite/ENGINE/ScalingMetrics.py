from builtins import staticmethod

__author__ = 'bloe'


class ScalingMetricValue:
    def __init__(self, timestamp, value):
        self.timestamp = timestamp
        self.value = value

    timestamp = None
    value = 0

class ScalingMetric:
    def __init__(self, metric_name):
        self.metric_name = metric_name
        self._values = []

    def add_value(self, metric_value):
        self._values.append(metric_value)

    metric_name = ""

class ScalingMetricInstance:
    def __init__(self, instance_uuid):
        self.instance_uuid = instance_uuid
        self._metrics = {}

    def add_metric(self, scaling_metric):
        if scaling_metric.metric_name not in self._metrics:
            self._metrics[scaling_metric.metric_name] = scaling_metric
        else:
            raise ValueError(
                "metric {} already exists in instance {}!".format(scaling_metric.metric_name, self.instance_uuid)
            )

    def metric_exists(self, metric_name):
        return metric_name in self._metrics

    def get_metric(self, metric_name):
        return self._metrics[metric_name]

    instance_uuid = ""

class ScalingMetricService:
    def __init__(self, service_name):
        self.service_name = service_name
        self._instances = {}

    def add_instance(self, instance):
        if instance.uuid not in self._instances:
            self._instances[instance.uuid] = instance
        else:
            raise ValueError("instance {} already exists!".format(instance.uuid))

    def get_instance(self, instance_uuid):
        return self._instances[self.instance.uuid]

    def instance_exists(self, instance_uuid):
        return instance_uuid in self._instances

    service_name = ""


class ScalingMetrics:
    def __init__(self):
        self._metrics_of_service = {}

    def add_metrics(self, metrics_message):
        scaling_metric_service = self._add_or_get_metrics_of_service(metrics_message)
        scaling_metric_instance = self._add_or_get_metric_instance(metrics_message, scaling_metric_service)
        scaling_metric = self._add_or_get_metric(metrics_message, scaling_metric_instance)
        self._create_scaling_values(metrics_message, scaling_metric)

    def _add_or_get_metrics_of_service(self, metrics_message):
        if metrics_message.service_name not in self._metrics_of_service:
            scaling_metric_service = ScalingMetricService(metrics_message.service_name)
            self._metrics_of_service[metrics_message.service_name] = scaling_metric_service
            return scaling_metric_service
        else:
            return self._metrics_of_service[metrics_message.service_name]

    @staticmethod
    def _add_or_get_metric_instance(self, metrics_message, scaling_metric_service):
        if scaling_metric_service.instance_exists(metrics_message.uuid):
            return scaling_metric_service.get_instance(metrics_message.uuid)
        else:
            scaling_metric_instance = ScalingMetricInstance(metrics_message.uuid)
            scaling_metric_service.add_instance(scaling_metric_instance)
            return scaling_metric_instance

    @staticmethod
    def _add_or_get_metric(self, metrics_message, scaling_metric_instance):
        if scaling_metric_instance.metric_exists(metrics_message.metric_name):
            return scaling_metric_instance.get_metric(metrics_message.metric_name)
        else:
            scaling_metric = ScalingMetric(metrics_message.metric_name)
            scaling_metric_instance.add_metric(scaling_metric)
            return scaling_metric

    @staticmethod
    def _create_scaling_values(self, metrics_message, scaling_metric):
        for metric_timestamped_value in metrics_message.metric_values:
            for timestamp, value in metric_timestamped_value.items():
                scaling_metric_value = ScalingMetricValue(timestamp, value)
                scaling_metric.add_value(scaling_metric_value)

    def cleanup_old_metrics(self, older_than_seconds):
        # TODO: implement delete of old metrics
        pass