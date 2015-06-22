__author__ = 'bloe'

from dynamite.ENGINE.MetricValue import MetricValue

class TestMetricValue:

    def test_init(self):
        timestamp = "2015-06-15T17:01:07.336000+0000"
        value = "value"
        metric_value = MetricValue(timestamp, value)
        assert metric_value.timestamp == timestamp
        assert metric_value.value == value
