from idlelib.SearchEngine import get

__author__ = 'brnr'

import argparse
import os
import platform
import yaml
import json
import requests
import etcd

from dynamite.INIT.DynamiteConfig import DynamiteConfig
from dynamite.INIT.DynamiteServiceHandler import DynamiteServiceHandler
from intervaltree import Interval, IntervalTree
from dynamite.GENERAL.FleetService import FleetService

from dynamite.GENERAL import ETCDCTL

# TODO: get all the running services from etcd
etcdctl = ETCDCTL.create_etcdctl("127.0.0.1:4001")

class Test(object):

    def to_json_string(self):

        instance_dict = {}

        for variable, value in self.__dict__.items():
            instance_dict[variable] = value

        return json.dumps(instance_dict)

    def __init__(self):
        self.x = 12
        self.y = 13


if __name__ == '__main__':
    x = Test()
    y = x.to_json_string()

    print(y)