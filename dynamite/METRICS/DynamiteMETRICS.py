__author__ = 'brnr'

from multiprocessing import Process
from dynamite.GENERAL.DynamiteExceptions import IllegalArgumentError
from dynamite.INIT.DynamiteConfig import DynamiteConfig
from dynamite.GENERAL import ETCDCTL


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

class DynamiteMETRICS(Process):

    etcd_endpoint = None
    etcdctl = None
    dynamite_config = None
    scaling_engine_metrics_communication_queue = None
    running = False

    def _do_stuff_with_config(self, dynamite_config):
        print(dynamite_config)

    def _init_etcdctl(self, arg_etcd_endpoint):
        etcdctl = ETCDCTL.create_etcdctl(arg_etcd_endpoint)

        if etcdctl is not None:
            return etcdctl
        else:
            return None

    def run(self):

        self.dynamite_config = DynamiteConfig(etcd_endpoint=self.etcd_endpoint)
        self.etcdctl = self._init_etcdctl(self.etcd_endpoint)

        # build path to get the needed application metrics
        application_metric_paths = []

        # /metrics/loadbalancer/metrics/response_time/2015-06-22T14:54:12.319Z
        # /metrics/webserver/e2213560-5b2f-4d2d-9d85-2cd878700259/metrics/cpu/cpu_user/2015-06-22T14:59:00.915Z

        self._do_stuff_with_config(self.dynamite_config)

        while self.running:
            self.running = False
            # get metrics from etcd
            # iterate through application_metric_paths list

            # create MetricsMessage and MetricValue

            # send MetricsMessage to scaling_engine_metris_communication queue
            # self.xxxQueue.put(product)

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