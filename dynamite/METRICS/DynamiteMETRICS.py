__author__ = 'brnr'

import time
import json
import logging
import etcd

from multiprocessing import Process

from dynamite.GENERAL.DynamiteExceptions import IllegalArgumentError
from dynamite.GENERAL import ETCDCTL
from dynamite.GENERAL.Retry import retry
from dynamite.GENERAL.EtcdHelper import EtcdHelper
from dynamite.INIT.DynamiteConfig import DynamiteConfig
from dynamite.METRICS.EtcdServiceMetricInformation import EtcdServiceMetricInformation
from dynamite.ENGINE.MetricsMessage import MetricsMessage
from dynamite.ENGINE.MetricValue import MetricValue

class DynamiteMETRICS(Process):

    _etcd_endpoint = None

    _scaling_engine_metrics_communication_queue = None
    _etcd_service_metric_information_instances = []
    _running = False

    _logger = None

    # service-name --> [metric-names]
    # this dictionary is used to keep track of service and metrics and helps to ensure there are no double entries
    _service_metrics_dictionary = {}

    _dynamite_config = None
    _exit_flag = None

    configuration = None
    etcdctl = None

    def __init__(self,
                 etcd_endpoint,
                 scaling_engine_metrics_communication_queue,
                 exit_flag
                 ):
        super(DynamiteMETRICS, self).__init__()
        self._exit_flag = exit_flag
        self._scaling_engine_metrics_communication_queue = scaling_engine_metrics_communication_queue
        self._etcd_endpoint = etcd_endpoint

    def run(self):
        try:
            self._logger = logging.getLogger(__name__)
            self._dynamite_config = self.configuration or DynamiteConfig(etcd_endpoint=self._etcd_endpoint)
            self._logger.info("Initialized DynamiteMETRICS with configuration %s", str(self))
            self._running = True
            self.etcdctl = self.etcdctl or self._init_etcdctl(self._etcd_endpoint)
            self._create_etcd_service_metric_information_instances(self._dynamite_config)

            while self._running:
                self._get_metrics_from_etcd()
                time.sleep(1)
                if self._exit_flag.value == 1:
                    self._running = False
        finally:
            self._exit_flag.value = 1

    def _init_etcdctl(self, etcd_endpoint):
        etcdctl = ETCDCTL.create_etcdctl(etcd_endpoint)
        return etcdctl

    def _create_etcd_service_metric_information_instances(self, dynamite_config):
        for policy in dynamite_config.ScalingPolicy.get_scaling_policies():
            etcd_service_metric_information = EtcdServiceMetricInformation(
                policy.service_type,
                policy.metric,
                policy.metric_aggregated
            )
            self._etcd_service_metric_information_instances.append(etcd_service_metric_information)

    def _get_metrics_from_etcd(self):
        for metric_information in self._etcd_service_metric_information_instances:
            self._get_metrics_from_service_type(metric_information)

    def _get_metrics_from_service_type(self, metric_information):
        if metric_information.is_aggregated:
            path = EtcdHelper.build_etcd_path([self._dynamite_config.ETCD.metrics_base_path, metric_information.service_type])
            self._get_metrics_from_instance("", path, metric_information)
        else:
            uuid_paths = self._get_instance_uuid_paths(metric_information.service_type)
            for uuid_path in uuid_paths:
                uuid = self._get_key_name_from_etcd_path(uuid_path)
                path = EtcdHelper.build_etcd_path([self._dynamite_config.ETCD.metrics_base_path, metric_information.service_type])
                self._get_metrics_from_instance(uuid, path, metric_information)

    def _get_metrics_from_instance(self, uuid, path_to_service_type, metric_information):
        metric_name = metric_information.metric_name

        metrics_path = EtcdHelper.build_etcd_path([path_to_service_type, uuid, metric_name])

        try:
            metric_folder = self.etcdctl.read(metrics_path, recursive=True, sorted=True)
            values = []
            for timestamp_node in metric_folder.children:
                if timestamp_node.value is not None:
                    value = self._read_value_from_etcd_node(timestamp_node, metric_information)
                    values.append(value)
                    self._delete_key_in_etcd(timestamp_node.key)
            if len(values) > 0:
                self._create_and_send_metrics_message(metric_information, uuid, values)
            else:
                self._logger.debug("No metrics found for metric {} in path {}".format(metric_name, metrics_path))
        except etcd.EtcdKeyNotFound:
            self._logger.debug("Could not find etcd key of metric %s in path %s", metric_name, metrics_path)

    @retry(Exception, tries=5, delay=1, backoff=2, logger=logging.getLogger(__name__))
    def _delete_key_in_etcd(self, key):
        self.etcdctl.delete(key)

    @staticmethod
    def _get_key_name_from_etcd_path(path):
        path_parts = path.split("/")
        if len(path_parts) < 1:
            raise ValueError("Cannot get key name from too short path {}".format(path))
        return path_parts[-1]

    def _read_value_from_etcd_node(self, etcd_node, metric_information):
        timestamp = self._get_key_name_from_etcd_path(etcd_node.key)
        value = etcd_node.value

        if metric_information.in_value_path is None:
            value = float(value)
        else:
            value = self._read_value_from_json(value, metric_information.in_value_path)

        return MetricValue(timestamp, value)

    def _read_value_from_json(self, json_string, in_value_path):
        # metric name will be like: response_time.time_backend_response.p95
        json_dict = json.loads(json_string)
        return json_dict[in_value_path]

    def _read_value_from_recursive_dict(self, dict, path):
        path_parts = path.split(".")
        if len(path_parts) < 1:
            raise ValueError("Could not read from dictionary {}, access path was {}".format(repr(dict)), path)
        if len(path_parts) == 1:
            return float(dict[path_parts[0]])
        return self._read_value_from_recursive_dict(dict[path_parts[0]], path_parts[1:])

    def _get_instance_uuid_paths(self, service_type):
        try:
            service_type_path = EtcdHelper.build_etcd_path([
                self._dynamite_config.ETCD.metrics_base_path,
                service_type
            ])
            uuid_nodes = self.etcdctl.read(service_type_path)

            uuid_paths = []
            for uuid_node in uuid_nodes.children:
                uuid_paths.append(uuid_node.key)
            return uuid_paths

        except etcd.EtcdKeyNotFound:
            self._logger.warn("Metrics path does not exist in etcd: {}".format(repr(service_type_path)))
            return []

    def _create_and_send_metrics_message(self, metric_information, uuid, values):
            metrics_message = MetricsMessage(
                metric_information.service_type,
                uuid,
                values,
                metric_information.get_full_metric_name()
            )

            self._logger.debug("Putting metrics message on scaling engine metrics communication queue: {}"
                               .format(repr(metrics_message)))
            self._scaling_engine_metrics_communication_queue.put(metrics_message)

    def stop(self):
        self._running = False

    def __repr__(self):
        return "DynamiteMETRICS(" \
               "etcd_endpoint=\"{}\", " \
               "scaling_engine_metrics_communication_queue=\"{}\", " \
               .format(
                    self._etcd_endpoint,
                    repr(self._scaling_engine_metrics_communication_queue),
               )

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