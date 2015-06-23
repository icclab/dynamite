__author__ = 'brnr'

import time
import json

from multiprocessing import Process

from dynamite.GENERAL.DynamiteExceptions import IllegalArgumentError
from dynamite.GENERAL import ETCDCTL
from dynamite.INIT.DynamiteConfig import DynamiteConfig
from dynamite.METRICS.EtcdServiceMetricInformation import EtcdServiceMetricInformation
from dynamite.ENGINE.MetricsMessage import MetricsMessage
from dynamite.ENGINE.MetricValue import MetricValue

class DynamiteMETRICS(Process):

    etcd_endpoint = None
    etcdctl = None
    dynamite_config = None
    scaling_engine_metrics_communication_queue = None
    etcd_service_metric_information_instances = []
    running = False

    # service-name --> [metric-names]
    # this dictionary is used to keep track of service and metrics and helps to ensure there are no double entries
    service_metrics_dictionary = {}

    def _init_etcdctl(self, etcd_endpoint):
        etcdctl = ETCDCTL.create_etcdctl(etcd_endpoint)

        if etcdctl is not None:
            return etcdctl
        else:
            return None

    def _etcd_get_uuids(self, metrics_base_path):
        r = self.etcdctl.read(metrics_base_path, recursive=True, sorted=True)

        uuids = []

        for child in r.children:
            uuid = child.key.split("/")[3]

            if uuid not in uuids:
                uuids.append(uuid)

        return uuids

    def _update_uuids(self):
        for instance in self.etcd_service_metric_information_instances:
            if not instance.is_aggregated:
                uuids = self._etcd_get_uuids(instance.metric_base_path)
                instance.uuids = uuids

    def _create_etcd_service_metric_information_instances(self, dynamite_config):
        metrics_path = dynamite_config.ETCD.metrics_base_path

        for policy_name, policy in dynamite_config.ScalingPolicy.__dict__.items():

            service_name = policy.service
            metric_name = policy.metric

            double_entry = False

            if service_name in self.service_metrics_dictionary:
                metrics = self.service_metrics_dictionary[service_name]

                if metric_name in metrics:
                    double_entry = True
                else:
                    self.service_metrics_dictionary[service_name].append(metric_name)
            else:
                self.service_metrics_dictionary[service_name] = [metric_name]

            if not double_entry:
                metrics_base_path = metrics_path + "/" + service_name

                is_aggregated = policy.metric_aggregated

                uuids = []

                # if metrics are not aggregated get the different uuids resp. instances
                if not is_aggregated:
                    uuids = self._etcd_get_uuids(metrics_base_path)

                # create metric path per EtcdServiceMetricInformation instance
                etcd_metric_paths = []

                if is_aggregated and service_name == "loadbalancer":
                    metric_and_detail = metric_name.split(".", 1)
                    metric = metric_and_detail[0]
                    detail = metric_and_detail[1]   # detail from json response

                    etcd_metric_path = metrics_base_path
                    etcd_metric_path += "/" + metric

                    etcd_metric_paths.append(etcd_metric_path)
                else:
                    metric = metric_name
                    etcd_metric_base_path = metrics_base_path

                    for uuid in uuids:
                        etcd_metric_path = etcd_metric_base_path + "/" + uuid + "/" + metric
                        etcd_metric_paths.append(etcd_metric_path)

                etcd_service_metric_information = EtcdServiceMetricInformation(service_name,
                                                                               metric_name,
                                                                               metrics_base_path,
                                                                               is_aggregated,
                                                                               uuids,
                                                                               etcd_metric_paths)

                self.etcd_service_metric_information_instances.append(etcd_service_metric_information)

    def run(self):

        self.dynamite_config = DynamiteConfig(etcd_endpoint=self.etcd_endpoint)
        self.etcdctl = self._init_etcdctl(self.etcd_endpoint)
        self._create_etcd_service_metric_information_instances(self.dynamite_config)

        while self.running:

            for instance in self.etcd_service_metric_information_instances:

                for etcd_metric_path in instance.etcd_metric_paths:

                    r = self.etcdctl.read(etcd_metric_path, recursive=True, sorted=True)

                    metric_values = []
                    uuid = None
                    value = None

                    # one child is represents one metric (key and value)
                    for child in r.children:

                        if child.value is not None:
                            timestamp = child.key.split("/")[-1]
                            value = child.value

                            if instance.service_name == "loadbalancer":
                                # metric name will be like: response_time.time_backend_response.p95
                                metric_from_json = instance.metric_name.split(".", 1)[-1]
                                response_json = json.loads(value)
                                value = response_json[metric_from_json]
                            else:
                                value = float(value)
                                uuid = child.key.split("/")[3]

                            metric_value = MetricValue(timestamp, value)
                            metric_values.append(metric_value)

                            self.etcdctl.delete(child.key)

                    if len(metric_values) > 0:
                        metrics_message = MetricsMessage(instance.service_name,
                                                         uuid,
                                                         metric_values,
                                                         instance.metric_name)

                        self.scaling_engine_metrics_communication_queue.put(metrics_message)

            time.sleep(1)

    def __init__(self, etcd_endpoint, scaling_engine_metrics_communication_queue):
        super(DynamiteMETRICS, self).__init__()

        if etcd_endpoint is not None and isinstance(etcd_endpoint, str):
            self.etcd_endpoint = etcd_endpoint

        else:
            raise IllegalArgumentError("Error: argument <etcd_endpoint> needs to be of type <str>")

        self.scaling_engine_metrics_communication_queue = scaling_engine_metrics_communication_queue

        self.running = True

if __name__ == '__main__':
    dynamite_metrics = DynamiteMETRICS("127.0.0.1:4001", None)
    dynamite_metrics.start()


# the folder 'response_time' (could) contain a bunch of entries
# /metrics/loadbalancer/metrics/response_time/2015-06-22T14:54:12.319Z

# answer from loadbalancer
# {
#     "@version":"1",
#     "@timestamp":"2015-06-22T14:54:12.319Z",
#     "message":"0a556865a3d9",
#     "time_backend_response.count":9,
#     "time_backend_response.rate_1m":0.0,
#     "time_backend_response.rate_5m":0.0,
#     "time_backend_response.rate_15m":0.0,
#     "time_backend_response.min":0.0,
#     "time_backend_response.max":699.0,
#     "time_backend_response.stddev":16.57579754980927,
#     "time_backend_response.mean":224.22222222222223,
#     "time_backend_response.p1":0.0,
#     "time_backend_response.p5":0.0,
#     "time_backend_response.p10":0.0,
#     "time_backend_response.p90":699.0,
#     "time_backend_response.p95":699.0,
#     "time_backend_response.p99":699.0,
#     "time_backend_response.p100":699.0,
#     "metric_period":"short_term",
#     "tags":["metric","shortterm","_grokparsefailure"]
# }
# '{"@version":"1","@timestamp":"2015-06-22T14:54:12.319Z","message":"0a556865a3d9","time_backend_response.count":9,"time_backend_response.rate_1m":0.0,"time_backend_response.rate_5m":0.0,"time_backend_response.rate_15m":0.0,"time_backend_response.min":0.0,"time_backend_response.max":699.0,"time_backend_response.stddev":16.57579754980927,"time_backend_response.mean":224.22222222222223,"time_backend_response.p1":0.0,"time_backend_response.p5":0.0,"time_backend_response.p10":0.0,"time_backend_response.p90":699.0,"time_backend_response.p95":699.0,"time_backend_response.p99":699.0,"time_backend_response.p100":699.0,"metric_period":"short_term","tags":["metric","shortterm","_grokparsefailure"]}'

# the folder 'cpu_user' (could) contain a bunch of entries
# /metrics/webserver/e2213560-5b2f-4d2d-9d85-2cd878700259/metrics/cpu/cpu_user/2015-06-22T14:59:00.915Z
# value