__author__ = 'bloe'

from dynamite.ENGINE.RunningServicesRegistry import RunningServicesRegistry
from dynamite.GENERAL.FleetService import FleetService

class TestRunningServicesRegistry:

    service_name_1 = "service1"
    service_name_2 = "service2"

    def test_initialize_from_service_dictionary(self):
        registry = RunningServicesRegistry()
        service1 = FleetService("service1",
                                path_on_filesystem=None,
                                unit_file_details_json_dict=None,
                                service_details_dynamite_config=None,
                                is_template=None,
                                service_announcer=None,
                                used_port_numbers=None)
        service1.fleet_service_instances = {"service1@0":None, "service1@1": None}
        service2 = FleetService("service2",
                                path_on_filesystem=None,
                                unit_file_details_json_dict=None,
                                service_details_dynamite_config=None,
                                is_template=None,
                                service_announcer=None,
                                used_port_numbers=None)
        service2.fleet_service_instances = {"service2@0":None, "service2@1": None, "service2@2":None}
        service_dict = {"service1": service1, "service2": service2}
        registry.initialize_from_service_dictionary(service_dict)

        assert registry.number_of_running_instances_of_service("service1") == 2
        assert registry.number_of_running_instances_of_service("service2") == 3

    def test_add_running_service(self):
        registry = RunningServicesRegistry()
        assert registry.number_of_running_instances_of_service(self.service_name_1) == 0
        registry.add_running_service(self.service_name_1)
        assert registry.number_of_running_instances_of_service(self.service_name_1) == 1
        registry.add_running_service(self.service_name_1)
        assert registry.number_of_running_instances_of_service(self.service_name_1) == 2

        assert registry.number_of_running_instances_of_service(self.service_name_2) == 0
        registry.add_running_service(self.service_name_2)
        assert registry.number_of_running_instances_of_service(self.service_name_2) == 1

    def test_remove_running_service(self):
        registry = RunningServicesRegistry()
        assert registry.number_of_running_instances_of_service(self.service_name_1) == 0
        assert registry.number_of_running_instances_of_service(self.service_name_2) == 0

        registry.add_running_service(self.service_name_1)
        registry.add_running_service(self.service_name_2)
        registry.add_running_service(self.service_name_2)
        registry.add_running_service(self.service_name_2)
        registry.remove_running_service(self.service_name_1)
        registry.remove_running_service(self.service_name_2)
        assert registry.number_of_running_instances_of_service(self.service_name_1) == 0
        assert registry.number_of_running_instances_of_service(self.service_name_2) == 2
