__author__ = 'bloe'

from dynamite.ENGINE.RunningServicesRegistry import RunningServicesRegistry
from dynamite.ENGINE.ScalingAction import ScalingAction, DynamiteScalingCommand
from unittest.mock import MagicMock
import pytest

class TestRunningServicesRegistry:

    service_name_1 = "service1"
    service_name_2 = "service2"
    non_existing_service_name = "non_existing_service"

    @classmethod
    def setup_class(cls):
        service1 = MagicMock()
        service1.name = "service1"

        service1.fleet_service_instances = {"service1@0": None, "service1@1": None}
        service2 = MagicMock()
        service2.name = "service2"

        service2.fleet_service_instances = {"service2@0": None, "service2@1": None, "service2@2": None}
        cls.service_dict = {"service1": service1, "service2": service2}

    def test_initialize_from_service_dictionary(self):
        registry = RunningServicesRegistry(self.service_dict)

        assert registry.number_of_running_instances_of_service("service1") == 2
        assert registry.number_of_running_instances_of_service("service2") == 3

    def test_add_running_service(self):
        registry = RunningServicesRegistry({})
        assert registry.number_of_running_instances_of_service(self.service_name_1) == 0
        registry.add_running_service(self.service_name_1)
        assert registry.number_of_running_instances_of_service(self.service_name_1) == 1
        registry.add_running_service(self.service_name_1)
        assert registry.number_of_running_instances_of_service(self.service_name_1) == 2

        assert registry.number_of_running_instances_of_service(self.service_name_2) == 0
        registry.add_running_service(self.service_name_2)
        assert registry.number_of_running_instances_of_service(self.service_name_2) == 1

    def test_add_running_service_non_existing(self):
        registry = RunningServicesRegistry({})
        registry.add_running_service(self.non_existing_service_name)
        assert registry.number_of_running_instances_of_service(self.non_existing_service_name) == 1

    def test_remove_running_service(self):
        registry = RunningServicesRegistry({})
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

    def test_remove_running_service_non_existing(self):
        with pytest.raises(ValueError):
            registry = RunningServicesRegistry({})
            assert registry.number_of_running_instances_of_service(self.service_name_1) == 0
            assert registry.number_of_running_instances_of_service(self.service_name_2) == 0

            registry.remove_running_service(self.non_existing_service_name)

    def test_remove_running_service_none_running(self):
        with pytest.raises(ValueError):
            registry = RunningServicesRegistry({})
            assert registry.number_of_running_instances_of_service(self.service_name_1) == 0
            assert registry.number_of_running_instances_of_service(self.service_name_2) == 0

            registry.remove_running_service(self.service_name_1)

    def test_scaling_action_allowed(self):
        self.service_dict[self.service_name_1].service_config_details = MagicMock()
        self.service_dict[self.service_name_1].service_config_details.max_instance = 5
        self.service_dict[self.service_name_1].service_config_details.min_instance = 2

        self.service_dict[self.service_name_2].service_config_details = MagicMock()
        self.service_dict[self.service_name_2].service_config_details.max_instance = 3
        self.service_dict[self.service_name_2].service_config_details.min_instance = 1

        registry = RunningServicesRegistry(self.service_dict)

        # service2 has 3 instances initially, max is 3
        scaling_action_service2 = ScalingAction(self.service_name_2)
        scaling_action_service2.command = DynamiteScalingCommand.SCALE_UP
        result = registry.scaling_action_allowed(scaling_action_service2)
        assert result is False

        scaling_action_service2.command = DynamiteScalingCommand.SCALE_DOWN
        result = registry.scaling_action_allowed(scaling_action_service2)
        assert result is True

        # service1 has 2 instances initially, min is 2
        scaling_action_service1 = ScalingAction(self.service_name_1)
        scaling_action_service1.command = DynamiteScalingCommand.SCALE_DOWN
        result = registry.scaling_action_allowed(scaling_action_service1)
        assert result is False
        scaling_action_service1.command = DynamiteScalingCommand.SCALE_UP
        result = registry.scaling_action_allowed(scaling_action_service1)
        assert result is True

    def test_scaling_action_allowed_with_unknown_service(self):
        with pytest.raises(ValueError):
            registry = RunningServicesRegistry(self.service_dict)
            scaling_action_service1 = ScalingAction(self.non_existing_service_name)
            scaling_action_service1.command = DynamiteScalingCommand.SCALE_DOWN
            registry.scaling_action_allowed(scaling_action_service1)

    def test_scaling_action_allowed_with_invalid_command(self):
        with pytest.raises(ValueError):
            registry = RunningServicesRegistry(self.service_dict)
            scaling_action_service1 = ScalingAction(self.service_name_1)
            scaling_action_service1.command = "scale_UP"
            registry.scaling_action_allowed(scaling_action_service1)

    def test_scaling_action_allowed_without_min_max_specified(self):
        self.service_dict[self.service_name_1].service_config_details = MagicMock()
        self.service_dict[self.service_name_1].service_config_details.max_instance = 5
        self.service_dict[self.service_name_1].service_config_details.min_instance = None

        self.service_dict[self.service_name_2].service_config_details = MagicMock()
        self.service_dict[self.service_name_2].service_config_details.max_instance = None
        self.service_dict[self.service_name_2].service_config_details.min_instance = 1

        registry = RunningServicesRegistry(self.service_dict)

        # service2 has 3 instances initially, max is undefined
        scaling_action_service2 = ScalingAction(self.service_name_2)
        scaling_action_service2.command = DynamiteScalingCommand.SCALE_UP
        result = registry.scaling_action_allowed(scaling_action_service2)
        assert result is True

        scaling_action_service2.command = DynamiteScalingCommand.SCALE_DOWN
        result = registry.scaling_action_allowed(scaling_action_service2)
        assert result is True

        # service1 has 2 instances initially, min is undefined
        scaling_action_service1 = ScalingAction(self.service_name_1)
        scaling_action_service1.command = DynamiteScalingCommand.SCALE_DOWN
        result = registry.scaling_action_allowed(scaling_action_service1)
        assert result is True
        scaling_action_service1.command = DynamiteScalingCommand.SCALE_UP
        result = registry.scaling_action_allowed(scaling_action_service1)
        assert result is True

    def test_scaling_action_allowed_scale_below_zero(self):
        self.service_dict[self.service_name_1].service_config_details = MagicMock()
        self.service_dict[self.service_name_1].service_config_details.max_instance = None
        self.service_dict[self.service_name_1].service_config_details.min_instance = 2
        self.service_dict[self.service_name_1].fleet_service_instances = {}

        registry = RunningServicesRegistry(self.service_dict)

        scaling_action_service1 = ScalingAction(self.service_name_1)
        scaling_action_service1.command = DynamiteScalingCommand.SCALE_DOWN
        result = registry.scaling_action_allowed(scaling_action_service1)
        assert result is False
