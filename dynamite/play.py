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

for i in range(3):
    print(i+1)
