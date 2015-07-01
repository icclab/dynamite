__author__ = 'bloe'

import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

import argparse
import time

from dynamite.GENERATOR.Configuration.MetricsGeneratorConfiguration import MetricsGeneratorConfiguration
from dynamite.GENERATOR.WriteEventGenerator import WriteEventGenerator
from dynamite.GENERATOR.EventWriter import EventWriter

class MetricsGenerator:

    DEFAULT_CONFIG_PATH = os.path.realpath(__file__) + "/generator.json"

    _config_path = None
    _configuration = None
    _generated_events = []

    def __init__(self):
        self._config_path = self.DEFAULT_CONFIG_PATH
        self._configuration = None
        self._generated_events = []

    def run(self):
        self._parse_arguments()
        self._parse_config()
        self._generate()
        writer = EventWriter(self._configuration)
        self._register_services(writer)
        self._sort_events_by_time()
        self._write_events(writer)

    def _parse_arguments(self):
        parser = argparse.ArgumentParser()

        parser.add_argument("--config_file", "-c",
                            help="Define Config-File to be used. Default: " + self.DEFAULT_CONFIG_PATH,
                            nargs='?',
                            default=self.DEFAULT_CONFIG_PATH)
        arguments = parser.parse_args()
        self._config_path = arguments.config_file

    def _parse_config(self):
        if not os.path.isfile(self._config_path):
            raise ValueError("Could not find file in path %s", self._config_path)

        file = open(self._config_path)
        file_contents = file.read()
        self._configuration = MetricsGeneratorConfiguration.from_json(file_contents)

    def _generate(self):
        event_generator = WriteEventGenerator()

        for resource in self._configuration.resources:
            self._generated_events.extend(event_generator.create_events_for_resource(resource))

    def _register_services(self, event_writer):
        for resource in self._configuration.resources:
            event_writer.register_service(resource)

    def _sort_events_by_time(self):
        self._generated_events.sort(key=lambda event: event.time)

    def _write_events(self, event_writer):
        for event in self._generated_events:
            event_writer.write_event(event)
            time.sleep(1)


if __name__ == '__main__':
    generator = MetricsGenerator()
    generator.run()
