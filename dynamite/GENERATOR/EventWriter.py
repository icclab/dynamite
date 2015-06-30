__author__ = 'bloe'

from dynamite.GENERAL import ETCDCTL
from dynamite.GENERAL.EtcdHelper import EtcdHelper

class EventWriter:

    _metrics_base_path = None
    _services_base_path = None
    _etcdctl = None

    def __init__(self, configuration):
        self._metrics_base_path = configuration.metrics_path
        self._services_base_path = configuration.services_path
        self._etcdctl = ETCDCTL.create_etcdctl(str(configuration.etcd_endpoint))

    def register_service(self, resource):
        path = self._build_services_path(resource)
        self._etcdctl.set(path, resource.instance_name)

    def _build_services_path(self, resource):
        return EtcdHelper.build_etcd_path([
            self._services_base_path,
            resource.service_type,
            resource.instance_uuid,
            "service_instance_name"
        ])

    def write_event(self, event):
        metrics_path = self._build_metrics_path(event)
        self._etcdctl.set(metrics_path, event.value)

    def _build_metrics_path(self, event):
        return EtcdHelper.build_etcd_path([
            self._metrics_base_path,
            event.resource.service_type,
            event.resource.instance_uuid,
            event.resource.metric_name,
            event.get_formatted_time()
        ])
