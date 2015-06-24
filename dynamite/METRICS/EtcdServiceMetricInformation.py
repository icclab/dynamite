__author__ = 'brnr'

class EtcdServiceMetricInformation(object):

    service_name = None         # from ScalingPolicy.<policy_name>
    metric_name = []           # from ScalingPolicy.metric
    metric_base_path = None     # from ETCD.metrics_base_path + service_name
    is_aggregated = None
    uuids = []                  # if not aggregated saves list of uuids
    etcd_metric_paths = None

    def __init__(self, service_name, metric_name, metric_base_path, is_aggregated, uuids, etcd_metric_paths):
        self.service_name = service_name
        self.metric_name = metric_name
        self.metric_base_path = metric_base_path
        self.is_aggregated = is_aggregated
        self.uuids = uuids
        self.etcd_metric_paths = etcd_metric_paths