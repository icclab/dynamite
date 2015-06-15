__author__ = 'bloe'

from datetime import datetime

class TimePeriod:
    def __init__(self, period_length_in_seconds):
        self.period_started = False
        self.period_start_time = None
        self.period_length_in_seconds = period_length_in_seconds

    def start_period(self, time):
        self.period_started = True
        self.period_start_time = time

    def start_period(self):
        self.start_period(datetime.now())

    def is_in_period(self, time):
        if not self.period_started:
            return False

        time_difference = time - self.period_start_time
        return time_difference.total_seconds() > self.period_length_in_seconds

    def is_in_period(self):
        return self.is_in_period(datetime.now(), self.period_length_in_seconds)

    def reset(self):
        self.period_started = False
        self.period_start_time = None
