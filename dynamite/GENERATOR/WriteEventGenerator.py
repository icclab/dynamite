__author__ = 'bloe'

import random
from datetime import timedelta
from dynamite.GENERATOR.WriteEvent import WriteEvent

class WriteEventGenerator:
    def __init__(self):
        pass

    def create_events_for_resource(self, resource):
        events = []
        for phase in resource.phases:
            events.extend(self._create_events_for_phase(phase, resource))
        return events

    def _create_events_for_phase(self, phase, resource):
        events = []
        event = WriteEvent()
        event.resource = resource
        event.time = phase.start_time
        event.value = self._generate_value(phase)
        events.append(event)

        time = phase.start_time
        end_time = time + timedelta(seconds=phase.duration_seconds)
        while time + timedelta(seconds=resource.write_interval) < end_time:
            time = time + timedelta(seconds=resource.write_interval)
            event = WriteEvent()
            event.resource = resource
            event.time = time
            event.value = self._generate_value(phase)
            events.append(event)

        return events

    def _generate_value(self, phase):
        min_value = float(phase.min_value)
        max_value = float(phase.max_value)
        return random.uniform(min_value, max_value)