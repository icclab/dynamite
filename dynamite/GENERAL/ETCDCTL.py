__author__ = 'brnr'

import requests
import etcd

class ETCDCTL(object):

    # Instance Variables
    etcdctl = None     # Is instance of ETCD class and used to communicate with etcd

    ip = None
    port = None

    etcd_base_url = None

    is_connected = None

    http_json_content_type_header = {'Content-Type': 'application/json'}

    def test_connection(self):
        request_url = self.etcd_base_url + "_etcd/config"

        try:
            response = requests.get(request_url)
            if response.status_code == 200:
                self.is_connected = True
                return True
            else:
                return False

        except requests.exceptions.ConnectionError:
            print("Error connecting to ETCD. Check if Endpoint is correct: " + self.ip + ":" + self.port)

    def get_etcdctl(self):
        if self.etcdctl is not None:
            return self.etcdctl
        else:
            return None

    def __init__(self, ip, port):

        # Maybe add some more validation checks for <ip> and <port> argument
        if ip is None or not isinstance(ip, str):
            raise ValueError("Error: <ip> argument needs to be of type <str> (e.g.: '127.0.0.1'")

        if port is None or not isinstance(port, str):
            raise ValueError("Error: <port> argument needs to be of type <str>")

        self.ip = ip
        self.port = port
        self.etcd_base_url = "http://" + self.ip + ":" + self.port + "/v2/keys/"

        if self.test_connection():
            self.etcdctl = etcd.Client(self.ip, int(self.port))
            #return self.etcd
        else:
            raise ConnectionError("Error connecting to ETCD. Check if Endpoint is correct: " + self.ip + ":" + self.port)