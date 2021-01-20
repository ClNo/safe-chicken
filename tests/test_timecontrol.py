from datetime import datetime

from dateutil.tz import tzlocal

from safechicken import timecontrol

time_control_1 = {
    "latitude": 47.03,
    "longitude": 7.31,
    "minutes_after_sunrise": 15,
    "minutes_after_sunset": 15
}

time_control_2 = {
    "latitude": 47.03,
    "longitude": 7.31,
    "minutes_after_sunrise": 0,
    "minutes_after_sunset": 0
}

time_control_3 = {
    "latitude": 47.03,
    "longitude": 7.31,
    "minutes_after_sunrise": -10,
    "minutes_after_sunset": -20
}


def test_timecontrol_1():
    door_times, door_times_converted =\
        timecontrol.recalc_door_times(time_control_1, datetime.fromisoformat('2020-01-01T09:00:00'), None, None)
    # door_times_converted =
    # {'sunrise_time': '08:17', 'sunset_time': '16:52', 'sunrise_open_time': '08:32', 'sunset_close_time': '17:07'}
    assert door_times_converted['sunrise_time'] == '08:17'
    assert door_times_converted['sunset_time'] == '16:52'
    assert door_times_converted['sunrise_open_time'] == '08:32'
    assert door_times_converted['sunset_close_time'] == '17:07'

    assert door_times['sunrise_time'] == datetime.fromisoformat('2020-01-01T08:17').astimezone(tz=tzlocal())
    assert door_times['sunset_time'] == datetime.fromisoformat('2020-01-01T16:52').astimezone(tz=tzlocal())
    assert door_times['sunrise_open_time'] == datetime.fromisoformat('2020-01-01T08:32').astimezone(tz=tzlocal())
    assert door_times['sunset_close_time'] == datetime.fromisoformat('2020-01-01T17:07').astimezone(tz=tzlocal())


def test_timecontrol_2():
    door_times, door_times_converted =\
        timecontrol.recalc_door_times(time_control_2, datetime.fromisoformat('2020-01-01T09:00:00'), None, None)
    assert door_times_converted['sunrise_time'] == '08:17'
    assert door_times_converted['sunset_time'] == '16:52'
    assert door_times_converted['sunrise_open_time'] == '08:17'
    assert door_times_converted['sunset_close_time'] == '16:52'

    door_times, door_times_converted =\
        timecontrol.recalc_door_times(time_control_3, datetime.fromisoformat('2020-01-01T09:00:00'), None, None)
    assert door_times_converted['sunrise_time'] == '08:17'
    assert door_times_converted['sunset_time'] == '16:52'
    assert door_times_converted['sunrise_open_time'] == '08:07'
    assert door_times_converted['sunset_close_time'] == '16:32'
