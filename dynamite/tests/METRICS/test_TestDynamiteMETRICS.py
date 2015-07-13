__author__ = 'bloe'

from unittest.mock import Mock
from multiprocessing import Queue, Value
from dynamite.tests.Fakes.ProcessSimulator import ProcessSimulator

from dynamite.METRICS.DynamiteMETRICS import DynamiteMETRICS
from dynamite.tests.Fakes.FakeEtcdClient import FakeEtcdClient
from dynamite.ENGINE.MetricsMessage import MetricsMessage
from dynamite.ENGINE.MetricValue import MetricValue

class TestDynamiteMETRICS:

    ETCD_ENDPOINT = ""

    etcd_content = {
        "services": {
            "webserver": {
                "apache-uuid-1": {
                    "service_instance_name": "apache_instance_name_1"
                }
            }
        },
        "metrics": {
            "webserver": {
                "apache-uuid-1": {
                    "cpu_user": {
                        "2015-06-26T09:52:07.680Z": "29",
                        "2015-06-26T09:52:08.680Z": "30",
                        "2015-06-26T09:52:09.680Z": "31"
                    }
                },
                "apache-uuid-2": {
                    "cpu_user": {
                        "2015-06-26T09:53:07.680Z": "20",
                        "2015-06-26T09:53:08.680Z": "21",
                        "2015-06-26T09:53:09.680Z": "22"
                    }
                }
            },
            "loadbalancer": {
                "response_time": {
                    "2015-06-22T14:54:12.319Z": '{"@version":"1","@timestamp":"2015-06-22T14:54:12.319Z","message":"0a556865a3d9","time_backend_response.count":9,"time_backend_response.rate_1m":0.0,"time_backend_response.rate_5m":0.0,"time_backend_response.rate_15m":0.0,"time_backend_response.min":0.0,"time_backend_response.max":699.0,"time_backend_response.stddev":16.57579754980927,"time_backend_response.mean":224.22222222222223,"time_backend_response.p1":0.0,"time_backend_response.p5":0.0,"time_backend_response.p10":0.0,"time_backend_response.p90":699.0,"time_backend_response.p95":699.0,"time_backend_response.p99":699.0,"time_backend_response.p100":699.0,"metric_period":"short_term","tags":["metric","shortterm","_grokparsefailure"]}',
                    "2015-06-22T14:54:13.319Z": '{"@version":"1","@timestamp":"2015-06-22T14:54:13.319Z","message":"0a556865a3d9","time_backend_response.count":9,"time_backend_response.rate_1m":0.0,"time_backend_response.rate_5m":0.0,"time_backend_response.rate_15m":0.0,"time_backend_response.min":0.0,"time_backend_response.max":699.0,"time_backend_response.stddev":16.57579754980927,"time_backend_response.mean":224.22222222222223,"time_backend_response.p1":0.0,"time_backend_response.p5":0.0,"time_backend_response.p10":0.0,"time_backend_response.p90":699.0,"time_backend_response.p95":699.0,"time_backend_response.p99":699.0,"time_backend_response.p100":699.0,"metric_period":"short_term","tags":["metric","shortterm","_grokparsefailure"]}'
                }
            }
        }
    }

    def test_run(self):
        etcdctl_mock = FakeEtcdClient(self.etcd_content)
        config_mock = Mock()
        config_mock.ETCD = Mock()
        config_mock.ETCD.metrics_base_path = "/metrics"

        policies_mock = config_mock.ScalingPolicy
        policies_mock.scale_up = Mock()
        policies_mock.scale_up.service_type = "webserver"
        policies_mock.scale_up.metric = "cpu_user"
        policies_mock.scale_up.metric_aggregated = False

        policies_mock.scale_down = Mock()
        policies_mock.scale_down.service_type = "loadbalancer"
        policies_mock.scale_down.metric = "response_time.time_backend_response.p95"
        policies_mock.scale_down.metric_aggregated = True
        policies_mock.get_scaling_policies = Mock(return_value=[policies_mock.scale_up, policies_mock.scale_down])

        exit_flag = Value('i', 0)
        result_queue = Queue()
        metrics_component = DynamiteMETRICS(self.ETCD_ENDPOINT, result_queue, exit_flag)
        metrics_component.etcdctl = etcdctl_mock
        metrics_component.configuration = config_mock

        process_simulator = ProcessSimulator(metrics_component)
        process_simulator.start()

        expected_message_count = 3
        messages_by_instance_uuid = {}
        for message_nr in range(0, expected_message_count):
            result = result_queue.get()
            messages_by_instance_uuid[result.uuid] = result

        assert result_queue.empty() is True

        expected_message_apache1 = MetricsMessage(
            "webserver",
            "apache-uuid-1",
            [
                MetricValue("2015-06-26T09:52:07.680Z", 29),
                MetricValue("2015-06-26T09:52:08.680Z", 30),
                MetricValue("2015-06-26T09:52:09.680Z", 31)
            ],
            "cpu_user"
        )
        assert messages_by_instance_uuid["apache-uuid-1"] == expected_message_apache1

        expected_message_apache2 = MetricsMessage(
            "webserver",
            "apache-uuid-2",
            [
                MetricValue("2015-06-26T09:53:07.680Z", 20),
                MetricValue("2015-06-26T09:53:08.680Z", 21),
                MetricValue("2015-06-26T09:53:09.680Z", 22)
            ],
            "cpu_user"
        )
        assert messages_by_instance_uuid["apache-uuid-2"] == expected_message_apache2

        expected_message_loadbalancer = MetricsMessage(
            "webserver",
            "apache-uuid-2",
            [
                MetricValue("2015-06-22T14:54:12.319Z", 699.0),
                MetricValue("2015-06-22T14:54:13.319Z", 699.0)
            ],
            "cpu_user"
        )
        assert messages_by_instance_uuid[""] == expected_message_loadbalancer
        process_simulator.stop()
        process_simulator.join()
