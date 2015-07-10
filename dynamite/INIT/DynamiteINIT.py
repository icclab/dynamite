__author__ = 'brnr'

from dynamite.INIT.DynamiteConfig import DynamiteConfig
from dynamite.INIT.DynamiteServiceHandler import DynamiteServiceHandler
from dynamite.GENERAL import ETCDCTL
from dynamite.GENERAL.DynamiteHelper import DYNAMITE_APPLICATION_STATUS

import etcd
import json
import requests
import logging

# used to initialize the dynamite application
# takes different action depending on the current status (read from etcd at startup) of the application
class DynamiteINIT(object):

    dynamite_config = None
    dynamite_service_handler = None

    etcdctl = None

    _logger = None

    def __init__(self, command_line_arguments):

        self._arg_config_path = command_line_arguments.config_path
        self._arg_service_folder = command_line_arguments.service_folder
        self._arg_etcd_endpoint = command_line_arguments.etcd_endpoint
        self._arg_fleet_endpoint = command_line_arguments.fleet_endpoint

        self._logger = logging.getLogger(__name__)
        self._logger.info("Initialized DynamiteINIT with configuration %s", str(self))

        self.etcdctl = self._init_etcdctl(self._arg_etcd_endpoint)

        if self.etcdctl is not None:
            dynamite_application_status = self._check_dynamite_application_status_etcd()

        if dynamite_application_status is None:
            self._logger.debug("Dynamite was in status <None> --> Initializing Dynamite")
            self._init_dynamite()
        elif dynamite_application_status == DYNAMITE_APPLICATION_STATUS.INITIALIZING:
            # If the application crashes in its 'initializing' state then everything saved in etcd as well as already
            # running fleet services get destroyed (for now. that process can be refined e.g. check how far the
            # initialization process went and continue from that point)
            self._logger.debug("Dynamite was in status <INITIALIZING> --> RE-Initializing Dynamite")
            self.re_init_dynamite()
        elif dynamite_application_status == DYNAMITE_APPLICATION_STATUS.RUNNING:
            self._logger.debug("Dynamite was in status <RUNNING> --> Recovering Dynamite")
            self.recover_dynamite()
        else:
            self._set_dynamite_application_status_etcd(DYNAMITE_APPLICATION_STATUS.NONE)

    def __repr__(self):
        return "DynamiteINIT(" \
               "arg_config_path='{}'," \
               "arg_service_folder='{}'," \
               "arg_etcd_endpoint='{}'".format(self._arg_config_path,
                                               self._arg_service_folder,
                                               self._arg_etcd_endpoint)

    def _init_etcdctl(self, arg_etcd_endpoint):
        etcdctl = ETCDCTL.create_etcdctl(arg_etcd_endpoint)

        if etcdctl is not None:
            return etcdctl
        else:
            return None

    def _check_dynamite_application_status_etcd(self):
        try:
            key = ETCDCTL.etcd_key_application_status
            res = self.etcdctl.read(key)

            if res.value in DYNAMITE_APPLICATION_STATUS.ALLOWED_VALUES:
                return res.value
        except etcd.EtcdKeyNotFound:
            return DYNAMITE_APPLICATION_STATUS.NONE

    def _set_dynamite_application_status_etcd(self, dynamite_application_state):
        if dynamite_application_state in DYNAMITE_APPLICATION_STATUS.ALLOWED_VALUES:
            key = ETCDCTL.etcd_key_application_status
            res = self.etcdctl.write(key, dynamite_application_state)
            return res
        else:
            return None

    def _init_dynamite(self, init_failed=False):
        self._set_dynamite_application_status_etcd(DYNAMITE_APPLICATION_STATUS.INITIALIZING)

        self.dynamite_config = DynamiteConfig(arg_config_path=self._arg_config_path,
                                              arg_service_folder_list=self._arg_service_folder,
                                              fleet_endpoint=self._arg_fleet_endpoint)

        # If the initialization process failed then first delete everything already saved to etcd and all
        # the running fleet services
        if init_failed:
            try:
                self.etcdctl.delete(ETCDCTL.etcd_key_base_path, recursive=True)
            except etcd.EtcdKeyNotFound:
                pass

            fleet_ip = self.dynamite_config.FleetAPIEndpoint.ip
            fleet_port = self.dynamite_config.FleetAPIEndpoint.port

            fleet_units_url = "http://" + fleet_ip + ":" + str(fleet_port) + "/fleet/v1/units"
            response = requests.get(fleet_units_url)

            response = json.loads(response.text)

            if len(response) > 0:
                for unit_detail in response["units"]:
                    fleet_service_name = unit_detail['name']

                    fleet_path_to_service = fleet_units_url + "/" + fleet_service_name
                    requests.delete(fleet_path_to_service)

        self.dynamite_service_handler = DynamiteServiceHandler(dynamite_config=self.dynamite_config)

        # save dynamite yaml config to etcd - this will be loaded if dynamite should crash and restart
        dynamite_config_yaml = self.dynamite_config.dynamite_yaml_config
        dynamite_config_json = json.dumps(dynamite_config_yaml)
        self.etcdctl.write(ETCDCTL.etcd_key_init_application_configuration, dynamite_config_json)

        # save the fleet services (including the currently running instances to etcd -
        #   they will be loaded if dynamite should crash and restart
        for service_name, fleet_service in self.dynamite_service_handler.FleetServiceDict.items():
            etcd_base_key = ETCDCTL.etcd_key_running_services + "/" + service_name

            fleet_service_dict = fleet_service.to_dict()

            # Write the json for each service instance in its own path and delete those entries from the original
            # dict which will be saved in its own path
            #   makes it easier to update single service instances (e.g. updating status of service)
            copy_dict = {}
            if "fleet_service_instances" in fleet_service_dict:
                service_instances = fleet_service_dict['fleet_service_instances']
                copy_dict = service_instances.copy() if service_instances is not None else {}

            if len(copy_dict) != 0:
                for fleet_service_instance_name, fleet_service_instance_dict in copy_dict.items():
                    fleet_service_instance_json = json.dumps(fleet_service_instance_dict)
                    fleet_service_instance_name = fleet_service_instance_dict['name']

                    etcd_instance_key = etcd_base_key + "/" + fleet_service_instance_name
                    self.etcdctl.write(etcd_instance_key, fleet_service_instance_json)

                    del fleet_service_dict['fleet_service_instances'][fleet_service_instance_name]

            etcd_template_key = etcd_base_key + "/" + ETCDCTL.etcd_name_fleet_service_template
            self.etcdctl.write(etcd_template_key, json.dumps(fleet_service_dict))

        self._set_dynamite_application_status_etcd(DYNAMITE_APPLICATION_STATUS.RUNNING)

    def recover_dynamite(self):
        self._set_dynamite_application_status_etcd(DYNAMITE_APPLICATION_STATUS.RECOVERING)

        self.dynamite_config = DynamiteConfig(etcd_endpoint=self._arg_etcd_endpoint, fleet_endpoint=self._arg_fleet_endpoint)
        self.dynamite_service_handler = DynamiteServiceHandler(dynamite_config=self.dynamite_config,
                                                               etcd_endpoint=self._arg_etcd_endpoint)

        self._set_dynamite_application_status_etcd(DYNAMITE_APPLICATION_STATUS.RUNNING)

    def re_init_dynamite(self):
        self._init_dynamite(init_failed=True)
