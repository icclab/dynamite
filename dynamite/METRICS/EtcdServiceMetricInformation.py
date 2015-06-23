__author__ = 'brnr'

class EtcdServiceMetricInformation(object):
    metric_base_path = None     # from ETCD.metrics_base_path + service_name
    is_aggregated = None
    uuids = []                  # if
    service_name                # from ScalingPolicy.<policy_name>