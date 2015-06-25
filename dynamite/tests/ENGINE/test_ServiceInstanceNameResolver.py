__author__ = 'bloe'

from unittest.mock import Mock, MagicMock
from dynamite.ENGINE.ServiceInstanceNameResolver import CachingServiceInstanceNameResolver, ServiceInstanceNameResolver
import pytest

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

    def read_etcd_content(self, path):
        path_parts = path.split("/")
        folder = self.etcd_content
        for path_part in path_parts:
            if path_part == "":
                continue
            folder = folder[path_part]

        result = Mock()
        result.children = []
        if isinstance(folder, dict):
            for key, subdict in folder.items():
                result.children.append(path + "/" + key)
        else:
            result.value = folder
        return result

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
        etcd_client_mock = Mock()
        etcd_client_mock.get = self.read_etcd_content
        etcd_client_mock.read = self.read_etcd_content
        uuid = "apache-uuid-1"

        resolver = ServiceInstanceNameResolver(etcd_client_mock)
        result = resolver.resolve(uuid)
        expected_result = "apache_instance_name_1"
        assert result == expected_result

    def test_etcd_resolve_nonexisting(self):
        etcd_client_mock = Mock()
        etcd_client_mock.get = self.read_etcd_content
        etcd_client_mock.read = self.read_etcd_content
        uuid = "apache-uuid-1"

        resolver = ServiceInstanceNameResolver(etcd_client_mock)
        result = resolver.resolve("nonexisting")
        assert result is None
