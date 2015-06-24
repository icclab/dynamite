__author__ = 'bloe'

import logging

class ServiceInstanceNameResolver:
    METRICS_BASE_URL = "/services/"
    INSTANCE_NAME_ETCD_KEY = "service_instance_name"

    def __init__(self, etcd_client):
        self._etcd_client = etcd_client

    def resolve(self, service_uuid):
        metrics_directory = self._etcd_client.get(self.METRICS_BASE_URL)

        for directory in metrics_directory.children:
            service_type_content = self._etcd_client.get(directory)
            for uuid_path in service_type_content.children:
                if uuid_path.endswith(service_uuid):
                    return self._etcd_client.read(uuid_path + "/" + self.INSTANCE_NAME_ETCD_KEY).value
        raise ValueError("Could not found service instance name of uuid {}".format(service_uuid))

class CachingServiceInstanceNameResolver:
    def __init__(self, service_instance_name_resolver):
        self._logger = logging.getLogger(__name__)
        self._service_instance_name_resolver = service_instance_name_resolver
        self._cache_by_uuid = {}

    def resolve(self, service_uuid):
        self._logger.debug("Resolve service instance name from uuid %s", service_uuid)

        if service_uuid in self._cache_by_uuid:
            instance_name = self._cache_by_uuid[service_uuid]
            self._logger.debug("Found service instance name %s of uuid %s in cache", instance_name, service_uuid)
            return instance_name

        instance_name = self._service_instance_name_resolver.resolve(service_uuid)
        self._cache_by_uuid[service_uuid] = instance_name
        self._logger.info("Resolved service instance name %s from uuid %s", instance_name, service_uuid)
        return instance_name
