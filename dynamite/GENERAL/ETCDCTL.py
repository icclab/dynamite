__author__ = 'brnr'

import requests
import etcd

# Instance Variables
etcdctl = None     # Is instance of ETCD class and used to communicate with etcd

ip = None
port = None

etcd_base_url = None

is_connected = None

etcd_key_base_path = "/_dynamite"

etcd_key_application_status = etcd_key_base_path + "/state/application_status"
etcd_key_init_application_configuration = etcd_key_base_path + "/init/application_configuration"
etcd_key_running_services = etcd_key_base_path + "/run/service"
etcd_name_fleet_service_template = "fleet_service_template"

# etcd_key_application_status = "/_dynamite/state/application_status"
# etcd_key_init_application_configuration = "_dynamite/init/application_configuration"
# etcd_key_running_services = "_dynamite/run/service"


def test_connection(etcd_client):
    try:
        etcd_client.get("/")
        return True
    except:
        return False


def create_etcdctl(etcd_endpoint):

    global etcd_base_url
    global etcdctl
    global ip
    global port

    if etcdctl is not None:
        return etcdctl

    if type(etcd_endpoint) != str:
        raise ValueError("Error: argument <arg_etcd_endpoint> needs to be of type <str>. Format: [IP]:[PORT]")

    try:
        etcd_endpoint.split(":")
    except ValueError:
        print("Wrong format of <arg_etcd_endpoint> argument. Format needs to be [IP]:[PORT]")
        return None

    if len(etcd_endpoint.split(":")) == 2:
        ip, port = etcd_endpoint.split(":")

        etcd_base_url = "http://" + ip + ":" + port + "/v2/keys/"

        etcdctl = etcd.Client(ip, int(port))
        if not test_connection(etcdctl):
            raise ConnectionError("Error connecting to ETCD. Check if Endpoint is correct: " + ip + ":" + str(port))
        return etcdctl
    else:
        raise ValueError("Error: Probably wrong format of argument <arg_etcd_endpoint>. Format: [IP]:[PORT]")


def get_etcdctl():

    global etcd_base_url
    global etcdctl

    return etcdctl