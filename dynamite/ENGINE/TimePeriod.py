__author__ = 'bloe'

from datetime import datetime, timedelta

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
        self.period_start_time = time or self._get_current_time()

    def is_in_period(self, time=None):
        if not self.period_started:
            return False

        if time is None:
            return self.is_in_period(time=self._get_current_time())
        else:
            time_difference = time - self.period_start_time
            return time_difference.total_seconds() <= self.period_length_in_seconds

    def calculate_period_end(self):
        if not self.period_started:
            raise ValueError("Cannot calculate end of period because period has not been started yet!")
        return self.period_start_time + timedelta(seconds=self.period_length_in_seconds)

    def reset(self):
        self.period_started = False
        self.period_start_time = None

    def __repr__(self):
        return "TimePeriod(period_started={},period_start_time={},period_length={})".format(
            repr(self.period_started),
            repr(self.period_start_time),
            repr(self.period_length_in_seconds)
        )
