__author__ = 'bloe'

class RunningServicesRegistry(object):
    def __init__(self):
        self._running_services = {}

    def add_running_service(self, service_name):
        if service_name not in self._running_services:
            self._running_services[service_name] = 0
        self._running_services[service_name] += 1

    def remove_running_service(self, service_name):
        if service_name not in self._running_services:
            raise ValueError("cannot remove instance of non existing service " + service_name)
        if self._running_services[service_name] < 1:
            raise ValueError("cannot decrease instance counter of services below zero. service-name: " + service_name)

        self._running_services[service_name] -= 1
