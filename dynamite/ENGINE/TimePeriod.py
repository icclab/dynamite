__author__ = 'bloe'

from datetime import datetime

class TimePeriod:
    def __init__(self, period_length_in_seconds, time_provider=datetime.now):
        self.period_started = False
        self.period_start_time = None
        self.period_length_in_seconds = period_length_in_seconds
        self._time_provider_method = time_provider

    def _get_current_time(self):
        return self._time_provider_method()

    def start_period(self, time=None):
        self.period_started = True
        if time is None:
            self.period_start_time = self._get_current_time()
        else:
            self.period_start_time = time

    def is_in_period(self, time=None):
        if not self.period_started:
            return False

        if time is None:
            return self.is_in_period(time=self._get_current_time())
        else:
            time_difference = time - self.period_start_time
            return time_difference.total_seconds() <= self.period_length_in_seconds

    def reset(self):
        self.period_started = False
        self.period_start_time = None
