__author__ = 'bloe'

class RunningServicesRegistry(object):
    def __init__(self):
        self._running_services = {}

    def initialize_from_service_dictionary(self, service_dictionary):
        for service_name, service in service_dictionary.items():
            for service_instance in service.fleet_service_instances.items():
                self.add_running_service(service_name)

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

    def number_of_running_instances_of_service(self, service_name):
        if service_name not in self._running_services:
            return 0

        return self._running_services[service_name]