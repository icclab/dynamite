__author__ = 'bloe'

class MetricsMessage(object):
    def __init__(self, service_name, uuid, metric_values, metric_name):
        self.service_name = service_name
        self.uuid = uuid
        self.metric_values = metric_values or []
        self.metric_name = metric_name

    @staticmethod
    def from_json():
        # TODO: parse metrics from json
        message = MetricsMessage(
            "",
            "",
            [],
            ""
        )
        return message

    service_name = ""
    uuid = ""
    metric_values = []
    metric_name = ""
