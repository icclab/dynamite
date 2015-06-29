__author__ = 'brnr'

class EtcdServiceMetricInformation(object):

    service_type = None
    metric_name = None
    is_aggregated = None
    in_value_path = None

    def __init__(self, service_type, metric_name, is_aggregated):
        self.service_type = service_type
        self.is_aggregated = is_aggregated

        if "." in metric_name:
            self._parse_in_value_path(metric_name)
        else:
            self.metric_name = metric_name

    def _parse_in_value_path(self, metric_name):
        path_parts = metric_name.split(".")
        if len(path_parts) < 2:
            raise ValueError("Metric name is not an in-value path {}".format(metric_name))
        self.metric_name = path_parts[0]
        self.in_value_path = ".".join(path_parts[1:])

    def get_full_metric_name(self):
        if self.in_value_path is not None:
            return self.metric_name + "." + self.in_value_path
        return self.metric_name

    def __repr__(self):
        return "EtcdServiceMetricInformation(service_type={},metric_name={},is_aggregated={},in_value_path={}".format(
            self.service_type,
            self.metric_name,
            self.is_aggregated,
            self.in_value_path
        )
