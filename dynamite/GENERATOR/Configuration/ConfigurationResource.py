__author__ = 'bloe'

from dynamite.GENERATOR.Configuration.ConfigurationHelper import ConfigurationHelper
from dynamite.GENERATOR.Configuration.Phase import Phase
import uuid

class ConfigurationResource:

    GENERATE_UUID_KEYWORD = "generate"
    NO_UUID_KEYWORD = "none"

    service_type = None
    instance_uuid = None
    instance_name = None
    write_interval = None
    metric_name = None
    metric_value_template = None
    phases = []

    def __init__(self):
        self.service_type = ""
        self.instance_uuid = ""
        self.instance_name = ""
        self.metric_name = ""
        self.metric_value_template = ""
        self.write_interval = 0
        self.phases = []

    @classmethod
    def generate_uuid(cls):
        generated_uuid = uuid.uuid4()
        return str(generated_uuid)

    @classmethod
    def from_dictionary(cls, global_write_interval, dictionary):
        resource = ConfigurationResource()
        resource.write_interval = ConfigurationHelper.dict_value_or_default(dictionary, "write_interval", global_write_interval)
        resource.metric_name = ConfigurationHelper.dict_value_or_fail(
            dictionary,
            "metric_name",
            "Metric name missing in resource configuration!"
        )
        resource.metric_value_template = ConfigurationHelper.dict_value_or_default(
            dictionary,
            "metric_value_template",
            None
        )
        resource.service_type = ConfigurationHelper.dict_value_or_fail(
            dictionary,
            "service_type",
            "Service type missing in resource configuration!"
        )
        resource.instance_uuid = ConfigurationHelper.dict_value_or_default(
            dictionary,
            "instance_uuid",
            cls.GENERATE_UUID_KEYWORD
        )
        if resource.instance_uuid == cls.GENERATE_UUID_KEYWORD:
            resource.instance_uuid = cls.generate_uuid()
        elif resource.instance_uuid == cls.NO_UUID_KEYWORD:
            resource.instance_uuid = ""

        resource.instance_name = ConfigurationHelper.dict_value_or_default(
            dictionary,
            "instance_name",
            None
        )
        phases_dictionary = ConfigurationHelper.dict_value_or_fail(
            dictionary,
            "phases",
            "There are no phases defined for a resource!"
        )
        previous_phase = None
        for phase_dictionary in phases_dictionary:
            phase = Phase.from_dictionary(phase_dictionary, previous_phase=previous_phase)
            previous_phase = phase
            resource.phases.append(phase)

        return resource
