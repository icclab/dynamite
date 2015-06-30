__author__ = 'bloe'

import json
import logging

from dynamite.GENERATOR.Configuration.ConfigurationResource import ConfigurationResource
from dynamite.GENERAL.ServiceEndpoint import ServiceEndpoint
from dynamite.GENERATOR.Configuration.ConfigurationHelper import ConfigurationHelper

class MetricsGeneratorConfiguration:

    DEFAULT_METRICS_PATH = "/metrics"
    DEFAULT_SERVICES_PATH = "/services"
    DEFAULT_WRITE_INTERVAL = 10
    DEFAULT_ETCD_ENDPOINT = "127.0.0.1:5672"

    _logger = None

    metrics_path = None
    services_path = None
    resources = None
    write_interval = None
    etcd_endpoint = None

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self.metrics_path = self.DEFAULT_METRICS_PATH
        self.services_path = self.DEFAULT_SERVICES_PATH
        self.write_interval = self.DEFAULT_WRITE_INTERVAL
        self.resources = []
        self.etcd_endpoint = None

    @classmethod
    def from_json(cls, json_string):
        parsed_json = json.loads(json_string)

        configuration = MetricsGeneratorConfiguration()
        configuration.metrics_path = ConfigurationHelper.dict_value_or_default(parsed_json, "metrics_base_path", cls.DEFAULT_METRICS_PATH)
        configuration.services_path = ConfigurationHelper.dict_value_or_default(parsed_json, "services_base_path", cls.DEFAULT_SERVICES_PATH)
        configuration.write_interval = ConfigurationHelper.dict_value_or_default(parsed_json, "write_interval", cls.DEFAULT_WRITE_INTERVAL)
        etcd_endpoint_string = ConfigurationHelper.dict_value_or_default(parsed_json, "etcd_endpoint", cls.DEFAULT_ETCD_ENDPOINT)
        configuration.etcd_endpoint = ServiceEndpoint.from_string(etcd_endpoint_string)

        resource_dictionaries = ConfigurationHelper.dict_value_or_default(parsed_json, "resources", [])
        configuration.resources = []
        for resource_dictionary in resource_dictionaries:
            resource = ConfigurationResource.from_dictionary(configuration.write_interval, resource_dictionary)
            configuration.resources.append(resource)
        return configuration
