__author__ = 'brnr'

import requests
import etcd

# Instance Variables
etcdctl = None     # Is instance of ETCD class and used to communicate with etcd

ip = None
port = None

etcd_base_url = None

is_connected = None

etcd_key_application_status = "/_dynamite/state/application_status"
etcd_key_init_application_configuration = "_dynamite/init/application_configuration"
etcd_key_running_services = "_dynamite/run/service"


def test_connection(etcd_base_url):
    global is_connected

    request_url = etcd_base_url + "_etcd/config"

    try:
        response = requests.get(request_url)
        if response.status_code == 200:
            is_connected = True
            return True
        else:
            return False

    except requests.exceptions.ConnectionError:
        print("Error connecting to ETCD. Check if Endpoint is correct: " + self.ip + ":" + self.port)


def create_etcdctl(ip_address, port_number):

    global etcd_base_url
    global etcdctl
    global ip
    global port

    if etcdctl is not None:
        return etcdctl
    else:
        if ip_address is None or not isinstance(ip_address, str):
            raise ValueError("Error: <ip> argument needs to be of type <str> (e.g.: '127.0.0.1'")

        if port_number is None or not isinstance(port_number, str):
            raise ValueError("Error: <port> argument needs to be of type <str>")

        ip = ip_address
        port = port_number

        etcd_base_url = "http://" + ip_address + ":" + port_number + "/v2/keys/"

        if test_connection(etcd_base_url):
            etcdctl = etcd.Client(ip_address, int(port_number))
        else:
            raise ConnectionError("Error connecting to ETCD. Check if Endpoint is correct: " + ip_address + ":" + port_number)

        if etcdctl is not None:
            return etcdctl
        else:
            return None


def get_etcdctl():

    global etcd_base_url
    global etcdctl

    if etcdctl is not None:
        return etcdctl
    else:
        return None