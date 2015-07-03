__author__ = 'bloe'

from dynamite.ENGINE.TimePeriod import TimePeriod
from datetime import datetime, timedelta
import pytest

class TestTimePeriod:

    @staticmethod
    def _get_time1():
        return datetime(2010, 10, 22, hour=15, minute=59, second=59, microsecond=100)

    @staticmethod
    def _get_time2():
        return datetime(1900, 3, 25, hour=22, minute=0, second=0, microsecond=999)

    def test_init(self):
        period_length = 464
        period = TimePeriod(period_length)

        assert period.period_started is False
        assert period.period_length_in_seconds == period_length
        assert period.period_start_time is None

    def test_start_period(self):
        start_time = self._get_time1()
        period = TimePeriod(30, time_provider=TestTimePeriod._get_time1)
        period.start_period()

        assert period.period_start_time == start_time
        assert period.period_started is True
        assert period.period_length_in_seconds == 30

    def test_start_period_with_start_time(self):
        start_time = self._get_time1()
        period = TimePeriod(90)
        period.start_period(start_time)

        assert period.period_start_time == start_time
        assert period.period_started is True
        assert period.period_length_in_seconds == 90

    def test_is_in_period_with_specific_time(self):
        start_time = self._get_time2()
        period_length = timedelta(seconds=30)
        period = TimePeriod(period_length.seconds, time_provider=self._get_time2)
        period.start_period()

        in_period_time_1 = start_time + timedelta(seconds=30)
        in_period_time_2 = start_time + timedelta(seconds=29)
        in_period_time_3 = start_time + timedelta(seconds=1)
        in_period_time_4 = start_time
        out_period_time_1 = start_time + timedelta(seconds=31)
        out_period_time_2 = start_time + timedelta(seconds=30, microseconds=1)

        assert period.is_in_period(time=in_period_time_1) is True
        assert period.is_in_period(time=in_period_time_2) is True
        assert period.is_in_period(time=in_period_time_3) is True
        assert period.is_in_period(time=in_period_time_4) is True
        assert period.is_in_period(time=out_period_time_1) is False
        assert period.is_in_period(time=out_period_time_2) is False

    def test_is_in_period_now(self):
        start_time = self._get_time1()
        period_length = timedelta(seconds=30)

        in_period_time_1 = start_time + timedelta(seconds=30)
        in_period_time_2 = start_time + timedelta(seconds=29)
        in_period_time_3 = start_time + timedelta(seconds=1)
        in_period_time_4 = start_time
        out_period_time_1 = start_time + timedelta(seconds=31)
        out_period_time_2 = start_time + timedelta(seconds=30, microseconds=1)

        period = TimePeriod(period_length.seconds, time_provider=lambda: in_period_time_1)
        period.start_period(start_time)
        assert period.is_in_period() is True

        period = TimePeriod(period_length.seconds, time_provider=lambda: in_period_time_2)
        period.start_period(start_time)
        assert period.is_in_period() is True

        period = TimePeriod(period_length.seconds, time_provider=lambda: in_period_time_3)
        period.start_period(start_time)
        assert period.is_in_period() is True

        period = TimePeriod(period_length.seconds, time_provider=lambda: in_period_time_4)
        period.start_period(start_time)
        assert period.is_in_period() is True

        period = TimePeriod(period_length.seconds, time_provider=lambda: out_period_time_1)
        period.start_period(start_time)
        assert period.is_in_period() is False

        period = TimePeriod(period_length.seconds, time_provider=lambda: out_period_time_2)
        period.start_period(start_time)
        assert period.is_in_period() is False

    def test_reset(self):
        period = TimePeriod(50, time_provider=self._get_time1)
        period.start_period(self._get_time1())
        period.reset()

        assert period.period_start_time is None
        assert period.period_started is False

    def test_calculate_period_end(self):
        period = TimePeriod(1000)
        start_time = self._get_time1()
        period.start_period(start_time)
        period_end = period.calculate_period_end()
        expected_end_time = start_time + timedelta(seconds=1000)
        assert period_end == expected_end_time

    def test_calculate_period_end_with_unstarted_period(self):
        with pytest.raises(ValueError):
            period = TimePeriod(1000)
            period_end = period.calculate_period_end()
            assert period_end is None
