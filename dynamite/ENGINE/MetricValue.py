__author__ = 'bloe'


class MetricValue:
    def __init__(self, timestamp, value):
        self._timestamp = timestamp
        self._value = value

    def _get_timestamp(self):
        return self._timestamp

    timestamp = property(_get_timestamp)

    def _get_value(self):
        return self._value

    value = property(_get_value)
