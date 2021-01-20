import datetime
from suntime import Sun, SunTimeException


def recalc_door_times(time_control_config, for_day, min_after_sunrise, min_after_sunset):
    sun = Sun(time_control_config['latitude'], time_control_config['longitude'])
    door_times = {}
    door_times['sunrise_time'] = sun.get_local_sunrise_time(for_day)
    door_times['sunset_time'] = sun.get_local_sunset_time(for_day)

    if min_after_sunrise is None:
        door_times['sunrise_open_time'] = door_times['sunrise_time'] + \
            datetime.timedelta(minutes=time_control_config['minutes_after_sunrise'])
    else:
        door_times['sunrise_open_time'] = door_times['sunrise_time'] + \
            datetime.timedelta(minutes=min_after_sunrise)

    if min_after_sunset is None:
        door_times['sunset_close_time'] = door_times['sunset_time'] + \
                                          datetime.timedelta(minutes=time_control_config['minutes_after_sunset'])
    else:
        door_times['sunset_close_time'] = door_times['sunset_time'] + \
                                          datetime.timedelta(minutes=min_after_sunset)

    # print('sunrise: {0}'.format(sunrise_time.strftime('%H:%M')))
    # print('sunset: {0}'.format(sunset_time.strftime('%H:%M')))

    door_times_converted = {}
    for elem in door_times:
        if type(door_times[elem]) == datetime.datetime:
            door_times_converted[elem] = door_times[elem].strftime('%H:%M')
        else:
            door_times_converted[elem] = door_times[elem]

    return door_times, door_times_converted
