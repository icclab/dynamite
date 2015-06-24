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
