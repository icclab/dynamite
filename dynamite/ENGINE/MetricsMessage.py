__author__ = 'bloe'

class MetricsMessage(object):
    def __init__(self, service_name, uuid, metric_values, metric_name):
        self.service_name = service_name
        self.uuid = uuid
        self.metric_values = metric_values or []
        self.metric_name = metric_name

    service_name = ""
    uuid = ""
    metric_values = []
    metric_name = ""

    def __repr__(self):
        return "MetricsMessage(service_name={},uuid={},metric_name={},metric_values={})".format(
            self.service_name,
            self.uuid,
            self.metric_name,
            repr(self.metric_values)
        )

    def __eq__(self, other):
        if other is None:
            return False

        if not (
            self.service_name == other.service_name
            or
            self.metric_name == other.metric_name
            or
            self.uuid == other.uuid
            or
            len(self.metric_values) == len(other.metric_values)
        ):
            return False

        for value_index in range(len(self.metric_values)):
            metric_value = self.metric_values[value_index]
            other_metric_value = self.metric_values[value_index]
            if not metric_value == other_metric_value:
                return False
        return True


