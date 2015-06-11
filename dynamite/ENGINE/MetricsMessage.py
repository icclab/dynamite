__author__ = 'bloe'

class MetricsMessage(object):
    def __init__(self, service_name, uuid, metric_values, metric_name):
        self._service_name = service_name
        self._uuid = uuid
        self._metric_values = metric_values
        self._metric_name = metric_name

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

    def _get_service_name(self):
        return self._service_name

    service_name = property(_get_service_name)

    def _get_uuid(self):
        return self._uuid

    uuid = property(_get_uuid)

    def _get_metric_values(self):
        return list(self._metric_values)

    metric_values = property(_get_metric_values)

    def _get_metric_name(self):
        return self._metric_name

    metric_name = property(_get_metric_name)
