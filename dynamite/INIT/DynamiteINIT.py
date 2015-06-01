__author__ = 'brnr'

from dynamite.INIT.DynamiteConfig import DynamiteConfig
from dynamite.INIT.DynamiteServiceHandler import DynamiteServiceHandler
from dynamite.GENERAL import ETCDCTL
from dynamite.GENERAL.DynamiteHelper import DYNAMITE_APPLICATION_STATUS
import etcd
import json


# used to initialize the dynamite application
# takes different action depending on the current status (read from etcd at startup) of the application
class DynamiteINIT(object):
    dynamite_config = None
    dynamite_service_handler = None

    etcdctl = None

    def init_etcdctl(self, arg_etcd_endpoint):
        etcdctl = ETCDCTL.create_etcdctl(arg_etcd_endpoint)

        if etcdctl is not None:
            return etcdctl
        else:
            return None

    def check_dynamite_application_status_etcd(self):
        try:
            key = ETCDCTL.etcd_key_application_status
            res = self.etcdctl.read(key)

            if res.value in DYNAMITE_APPLICATION_STATUS.ALLOWED_VALUES:
                return res.value
        except etcd.EtcdKeyNotFound:
            return DYNAMITE_APPLICATION_STATUS.NONE


    def set_dynamite_application_status_etcd(self, dynamite_application_state):
        if dynamite_application_state in DYNAMITE_APPLICATION_STATUS.ALLOWED_VALUES:
            key = ETCDCTL.etcd_key_application_status
            res = self.etcdctl.write(key, dynamite_application_state)
            return res
        else:
            return None


    def init_dynamite(self, arg_config_path, arg_service_folder):
        self.dynamite_config = DynamiteConfig(arg_config_path=arg_config_path,
                                              arg_service_folder_list=arg_service_folder)

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
            copy_dict = fleet_service_dict['fleet_service_instances'].copy()

            if len(copy_dict) != 0:
                for fleet_service_instance_name, fleet_service_instance_dict in copy_dict.items():
                    fleet_service_instance_json = json.dumps(fleet_service_instance_dict)
                    fleet_service_instance_name = fleet_service_instance_dict['name']

                    etcd_instance_key = etcd_base_key + "/" + fleet_service_instance_name
                    self.etcdctl.write(etcd_instance_key, fleet_service_instance_json)

                    del fleet_service_dict['fleet_service_instances'][fleet_service_instance_name]

            etcd_template_key = etcd_base_key + "/" + ETCDCTL.etcd_name_fleet_service_template
            self.etcdctl.write(etcd_template_key, json.dumps(fleet_service_dict))

    def recover_dynamite(self, etcd_endpoint):
        self.dynamite_config = DynamiteConfig(etcd_endpoint=etcd_endpoint)
        self.dynamite_service_handler = DynamiteServiceHandler(dynamite_config=self.dynamite_config,
                                                               etcd_endpoint=etcd_endpoint)


    def __init__(self, arg_config_path, arg_service_folder, arg_etcd_endpoint):
        # create etcd Client
        self.etcdctl = self.init_etcdctl(arg_etcd_endpoint)

        if self.etcdctl is not None:
            dynamite_application_status = self.check_dynamite_application_status_etcd()

        # TODO: if the status is initializing reset the things already saved in etcd
        if dynamite_application_status is None:
            self.set_dynamite_application_status_etcd(DYNAMITE_APPLICATION_STATUS.INITIALIZING)
            self.init_dynamite(arg_config_path, arg_service_folder)
            self.set_dynamite_application_status_etcd(DYNAMITE_APPLICATION_STATUS.RUNNING)
        elif dynamite_application_status == DYNAMITE_APPLICATION_STATUS.INITIALIZING:
            pass
        elif dynamite_application_status == DYNAMITE_APPLICATION_STATUS.RUNNING:
            self.set_dynamite_application_status_etcd(DYNAMITE_APPLICATION_STATUS.RECOVERING)
            self.recover_dynamite(arg_etcd_endpoint)
            self.set_dynamite_application_status_etcd(DYNAMITE_APPLICATION_STATUS.RUNNING)
        else:
            self.set_dynamite_application_status_etcd(DYNAMITE_APPLICATION_STATUS.NONE)



    def __str__(self):
        pass