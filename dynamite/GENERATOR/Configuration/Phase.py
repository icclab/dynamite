__author__ = 'bloe'

import dateutil.parser
from dynamite.GENERATOR.Configuration.ConfigurationHelper import ConfigurationHelper
from datetime import timedelta

class Phase:

    start_time = None
    duration_seconds = None
    min_value = None
    max_value = None

    def __init__(self):
        pass

    @classmethod
    def from_dictionary(cls, dictionary, previous_phase=None):
        phase = Phase()
        phase.duration_seconds = ConfigurationHelper.dict_value_or_default(dictionary, "duration_seconds", 60)
        phase.min_value = ConfigurationHelper.dict_value_or_default(dictionary, "min_value", 0)
        phase.max_value = ConfigurationHelper.dict_value_or_default(dictionary, "max_value", 100)
        if "start_time" in dictionary or previous_phase is None:
            start_time_string = ConfigurationHelper.dict_value_or_fail(
                dictionary,
                "start_time",
                "The first phase has to have a start_time attribute!"
            )
            phase.start_time = dateutil.parser.parse(start_time_string)
        else:
            phase.start_time = cls.calculate_start_time_depending_on_previous_phase(previous_phase)

        return phase

    @staticmethod
    def calculate_start_time_depending_on_previous_phase(previous_phase):
        if previous_phase.start_time is None:
            raise ValueError("The start_time of previous phases was not set!")
        return previous_phase.start_time + timedelta(seconds=previous_phase.duration_seconds)
