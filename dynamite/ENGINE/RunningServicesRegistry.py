__author__ = 'bloe'

from dynamite.EXECUTOR.DynamiteScalingCommand import DynamiteScalingCommand

class RunningServicesRegistry(object):
    def __init__(self, services_configuration):
        self._running_services = {}
        self._services_configuration = services_configuration
        self._initialize_from_service_dictionary(services_configuration)

    def _initialize_from_service_dictionary(self, service_dictionary):
        for service_name, service in service_dictionary.items():
            for service_instance in service.fleet_service_instances.items():
                self.add_running_service(service_name)

    def _initialize_running_service_if_not_exists(self, service_name):
        if service_name not in self._running_services:
            self._running_services[service_name] = 0

    def add_running_service(self, service_name):
        self._initialize_running_service_if_not_exists(service_name)
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

    def scaling_action_allowed(self, scaling_action):
        if scaling_action.service_name not in self._services_configuration:
            raise ValueError(
                "Could not find the service configuration of the service {}".format(scaling_action.service_name)
            )

        self._initialize_running_service_if_not_exists(scaling_action.service_name)
        service = self._services_configuration[scaling_action.service_name]
        scale_allowed_decision_methods = {
            DynamiteScalingCommand.SCALE_UP: self._scaleup_allowed,
            DynamiteScalingCommand.SCALE_DOWN: self._scaledown_allowed
        }
        if scaling_action.command not in scale_allowed_decision_methods:
            raise ValueError("The scaling action command {} is not supported!".format(scaling_action.command))

        scale_allowed_decision_method = scale_allowed_decision_methods[scaling_action.command]
        return scale_allowed_decision_method(service)

    def _scaleup_allowed(self, service):
        if service.service_config_details.max_instance is None:
            return True
        return service.service_config_details.max_instance > self.number_of_running_instances_of_service(service.name)

    def _scaledown_allowed(self, service):
        if service.service_config_details.min_instance is None:
            return True
        return service.service_config_details.min_instance < self.number_of_running_instances_of_service(service.name)
