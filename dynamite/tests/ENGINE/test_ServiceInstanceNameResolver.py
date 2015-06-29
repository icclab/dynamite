__author__ = 'bloe'

from unittest.mock import Mock, MagicMock

from dynamite.ENGINE.ServiceInstanceNameResolver import CachingServiceInstanceNameResolver, ServiceInstanceNameResolver
from dynamite.tests.Fakes.FakeEtcdClient import FakeEtcdClient


class TestCachingServiceInstanceNameReceiver:

    etcd_content = {
        "services": {
            "webserver": {
                "apache-uuid-1": {
                    "service_instance_name": "apache_instance_name_1"
                },
                "apache-uuid-2": {
                    "service_instance_name": "apache_instance_name_2"
                }
            },
            "loadbalancer": {
                "haproxy-uuid-1": {
                    "service_instance_name": "haproxy_instance_name_1"
                },
                "haproxy-uuid-2": {
                    "service_instance_name": "haproxy_instance_name_2"
                }
            }
        },
        "metrics": {}
    }

    def test_cached_resolve(self):
        resolver_mock = Mock()
        instance_name = "instance_name_of_service"

        resolver_mock.resolve = MagicMock(return_value=instance_name)
        uuid = "uuid-of-service"

        resolver = CachingServiceInstanceNameResolver(resolver_mock)
        result = resolver.resolve(uuid)

        resolver_mock.resolve.assert_called_once_with(uuid)
        assert instance_name == result

        resolver_mock.reset_mock()
        result = resolver.resolve(uuid)
        assert resolver_mock.resolve.call_count == 0
        assert instance_name == result

    def test_etcd_resolve(self):
        etcd_client_mock = FakeEtcdClient(self.etcd_content)
        uuid = "apache-uuid-1"

        resolver = ServiceInstanceNameResolver(etcd_client_mock)
        result = resolver.resolve(uuid)
        expected_result = "apache_instance_name_1"
        assert result == expected_result

    def test_etcd_resolve_nonexisting(self):
        etcd_client_mock = FakeEtcdClient(self.etcd_content)
        uuid = "apache-uuid-1"

        resolver = ServiceInstanceNameResolver(etcd_client_mock)
        result = resolver.resolve("nonexisting")
        assert result is None
