from datetime import datetime

from safechicken import timecontrol
from safechicken.controller import Controller


class Dispatcher:
    def __init__(self, current_datetime_iso):
        self.expired = 0
        self.erroro_code = 0
        self.err_str = ''
        self.command_out = {}
        self.current_datetime = datetime.fromisoformat(current_datetime_iso)

    # callback method
    def notify_force_expired(self):
        self.expired = 1

    # callback method
    def report_err(self, code, err_str):
        self.erroro_code = code
        self.err_str = err_str

    def clear_err(self):
        self.erroro_code = 0
        self.err_str = ''

    def command_changed(self, command_out):
        self.command_out = command_out

    def set_datetime_now(self, current_datetime_iso):
        self.current_datetime = datetime.fromisoformat(current_datetime_iso)

    def get_datetime_now(self):
        # separate method as it is used for testing
        return self.current_datetime


time_control_1 = {
    "latitude": 47.03,
    "longitude": 7.31,
    "minutes_after_sunrise": 15,
    "minutes_after_sunset": 15
}

controller_conf_1 = {
    "start_action_delay": 1.5,
    "force_time_expire_minutes": 180
}

expected_command_args = ['current', 'reason', 'next', 'next_time', 'reason_next']


def test_invalid_time():
    # test an invalid system clock (too old)
    dispatcher = Dispatcher('2019-12-31T23:00:00')
    controller = Controller()
    controller.init(controller_conf_1, dispatcher)
    controller.set_static_time('9:00', '18:00')
    controller.set_door_prio('static', 'static')
    controller.set_force_operation('auto', None)

    door_times, door_times_converted =\
        timecontrol.recalc_door_times(time_control_1, datetime.fromisoformat('2019-12-31T23:00:00'), None, None)
    assert door_times, 'Sun calculation (door_times) is not working'
    assert door_times_converted, 'Sun calculation (door_times) is not working'
    assert 'sunrise_open_time' in door_times_converted, 'Sun calculation (door_times) as no field "sunrise_open_time"'
    assert 'sunset_close_time' in door_times_converted, 'Sun calculation (door_times) as no field "sunset_close_time"'
    controller.set_sunbased_time(door_times_converted['sunrise_open_time'],
                                 door_times_converted['sunset_close_time'])

    assert dispatcher.erroro_code == 100, 'Date is invalid, but no error code set'

    for arg in expected_command_args:
        assert arg in dispatcher.command_out, 'Argument "{0}" not found in commant_out dict: {1}'.format(arg, dispatcher.command_out)
        assert dispatcher.command_out[arg] is None, 'Argument "{0}" has to be "None" because date is invalid: {1}'.format(arg, dispatcher.command_out)

    # now set a correct time
    dispatcher.set_datetime_now('2020-01-01T00:00:00')
    controller.recalc(systemtime_synced=True)

    assert dispatcher.erroro_code == 0, 'Date is valid now, error code should be cleared'

    for arg in ['next', 'next_time', 'reason_next']:
        assert arg in dispatcher.command_out, 'Argument "{0}" not found in commant_out dict: {1}'.format(arg, dispatcher.command_out)
        assert dispatcher.command_out[arg] is not None, 'Argument "{0}" has to be NOT "None" because date is valid: {1}'.format(arg, dispatcher.command_out)


def test_force_mode_static():
    # expect that the completeness of the results is already tested
    dispatcher = Dispatcher('2020-01-01T00:00:00')
    controller = Controller()
    controller.init(controller_conf_1, dispatcher)
    controller.set_static_time('9:00', '18:00')
    controller.set_door_prio('static', 'static')
    controller.set_force_operation('auto', None)

    # 1. set to static
    door_times, door_times_converted =\
        timecontrol.recalc_door_times(time_control_1, datetime.fromisoformat('2020-01-01T09:00:00'), None, None)
    controller.set_sunbased_time(door_times_converted['sunrise_open_time'],
                                 door_times_converted['sunset_close_time'])
    controller.recalc(systemtime_synced=True)

    assert dispatcher.command_out['current'] is None, '"current" should be set to none'
    assert dispatcher.command_out['reason'] is None, '"reason" should be set to none'
    assert dispatcher.command_out['next'] == 'open', '"next" should be set to "open"'
    assert dispatcher.command_out['reason_next'] == 'static', '"reason_next" should be set to "static"'
    assert dispatcher.command_out['next_time'] == datetime.fromisoformat('2020-01-01T09:00:00'),\
        '"next_time" should be set to "2020-01-01T09:00:00"'

    # 2. activate force mode open
    controller.set_force_operation('open', '2020-01-01T00:00:00')
    assert dispatcher.command_out['current'] == 'open', 'force mode set to "open", should be open now'
    # advance time within force_time_expire_minutes
    dispatcher.set_datetime_now('2020-01-01T02:59:00')
    controller.recalc()
    assert dispatcher.command_out['current'] == 'open', 'force mode set to "open", should STILL be open now'

    # 3. advance to timeout (after force_time_expire_minutes)
    dispatcher.set_datetime_now('2020-01-01T03:00:01')
    controller.recalc()
    assert dispatcher.command_out['current'] is None, 'force mode timeout. "current" should be None'
    assert dispatcher.command_out['next'] == 'open', '"next" should be set to "open"'
    assert dispatcher.command_out['reason_next'] == 'static', '"reason_next" should be set to "static"'
    assert dispatcher.command_out['next_time'] == datetime.fromisoformat('2020-01-01T09:00:00'),\
        '"next_time" should be set to "2020-01-01T09:00:00"'

    # 4. force open before static open
    dispatcher.set_datetime_now('2020-01-01T08:30:00')
    controller.set_force_operation('open', '2020-01-01T08:30:00')
    assert dispatcher.command_out['current'] is 'open', 'force mode set to "open", should be open now'
    assert dispatcher.command_out['next'] == 'open', '"next" should be set to "open"'
    assert dispatcher.command_out['reason_next'] == 'static', '"reason_next" should be set to "static"'

    # 5. force mode should be still active after static open, but next should be 'close'
    dispatcher.set_datetime_now('2020-01-01T09:01:00')
    controller.recalc()
    assert dispatcher.command_out['current'] is 'open', 'force mode set to "open", should be open now'
    assert dispatcher.command_out['next'] == 'close', '"next" should be set to "close"'
    assert dispatcher.command_out['reason_next'] == 'static', '"reason_next" should be set to "static"'
    assert dispatcher.command_out['next_time'] == datetime.fromisoformat('2020-01-01T18:00:00'),\
        '"next_time" should be set to "2020-01-01T18:00:00"'

    # 6. force mode timeout, static close should still be next
    dispatcher.set_datetime_now('2020-01-01T11:30:01')
    controller.recalc()
    assert dispatcher.command_out['current'] is None, 'force mode timeout. "current" should be None'
    assert dispatcher.command_out['next'] == 'close', '"next" should be set to "close"'
    assert dispatcher.command_out['reason_next'] == 'static', '"reason_next" should be set to "static"'
    assert dispatcher.command_out['next_time'] == datetime.fromisoformat('2020-01-01T18:00:00'),\
        '"next_time" should be set to "2020-01-01T18:00:00"'

    # 7. force close
    dispatcher.set_datetime_now('2020-01-01T17:00:00')
    controller.set_force_operation('close', '2020-01-01T17:00:00')
    assert dispatcher.command_out['current'] is 'close', 'force mode set to "open", should be close now'
    assert dispatcher.command_out['next'] == 'close', '"next" should be set to "close"'
    assert dispatcher.command_out['reason_next'] == 'static', '"reason_next" should be set to "static"'
    assert dispatcher.command_out['next_time'] == datetime.fromisoformat('2020-01-01T18:00:00'),\
        '"next_time" should be set to "2020-01-01T18:00:00"'

    # 8. advance after static close, force close still active
    dispatcher.set_datetime_now('2020-01-01T18:01:00')
    controller.recalc()
    assert dispatcher.command_out['current'] is 'close', 'force mode set to "open", should be close now'
    assert dispatcher.command_out['next'] == 'open', '"next" should be set to "open"'
    assert dispatcher.command_out['reason_next'] == 'static', '"reason_next" should be set to "static"'
    assert dispatcher.command_out['next_time'] == datetime.fromisoformat('2020-01-02T09:00:00'),\
        '"next_time" should be set to "2020-01-02T09:00:00"'

    # 9. set to auto
    controller.set_force_operation('auto', None)
    assert dispatcher.command_out['current'] is None, 'force mode set to "auto", "current" should be None'
    assert dispatcher.command_out['next'] == 'open', '"next" should be set to "open"'
    assert dispatcher.command_out['reason_next'] == 'static', '"reason_next" should be set to "static"'
    assert dispatcher.command_out['next_time'] == datetime.fromisoformat('2020-01-02T09:00:00'),\
        '"next_time" should be set to "2020-01-02T09:00:00"'


def test_sunbased_control():
    # expect that the completeness of the results is already tested
    dispatcher = Dispatcher('2020-01-01T00:00:00')
    controller = Controller()
    controller.init(controller_conf_1, dispatcher)
    controller.set_static_time('9:00', '18:00')
    controller.set_door_prio('sunbased', 'sunbased')
    controller.set_force_operation('auto', None)

    # 1. set to static
    door_times, door_times_converted =\
        timecontrol.recalc_door_times(time_control_1, datetime.fromisoformat('2020-01-01T09:00:00'), None, None)
    # door_times_converted =
    # {'sunrise_time': '08:17', 'sunset_time': '16:52', 'sunrise_open_time': '08:32', 'sunset_close_time': '17:07'}
    controller.set_sunbased_time(door_times_converted['sunrise_open_time'],
                                 door_times_converted['sunset_close_time'])
    controller.recalc(systemtime_synced=True)

    assert dispatcher.command_out['current'] is None, '"current" should be set to none'
    assert dispatcher.command_out['reason'] is None, '"reason" should be set to none'
    assert dispatcher.command_out['next'] == 'open', '"next" should be set to "open"'
    assert dispatcher.command_out['reason_next'] == 'sunbased', '"reason_next" should be set to "sunbased"'
    assert dispatcher.command_out['next_time'] == datetime.fromisoformat('2020-01-01T08:32:00'),\
        '"next_time" should be set to "2020-01-01T08:32:00"'

    # 2. activate force mode open
    controller.set_force_operation('open', '2020-01-01T00:00:00')
    assert dispatcher.command_out['current'] == 'open', 'force mode set to "open", should be open now'
    # advance time within force_time_expire_minutes
    dispatcher.set_datetime_now('2020-01-01T02:59:00')
    controller.recalc()
    assert dispatcher.command_out['current'] == 'open', 'force mode set to "open", should STILL be open now'

    # 3. advance to timeout (after force_time_expire_minutes)
    dispatcher.set_datetime_now('2020-01-01T03:00:01')
    controller.recalc()
    assert dispatcher.command_out['current'] is None, 'force mode timeout. "current" should be None'
    assert dispatcher.command_out['next'] == 'open', '"next" should be set to "open"'
    assert dispatcher.command_out['reason_next'] == 'sunbased', '"reason_next" should be set to "sunbased"'
    assert dispatcher.command_out['next_time'] == datetime.fromisoformat('2020-01-01T08:32:00'),\
        '"next_time" should be set to "2020-01-01T08:32:00"'

    # 4. force open before sunbased open
    dispatcher.set_datetime_now('2020-01-01T08:15:00')
    controller.set_force_operation('open', '2020-01-01T08:15:00')
    assert dispatcher.command_out['current'] is 'open', 'force mode set to "open", should be open now'
    assert dispatcher.command_out['next'] == 'open', '"next" should be set to "open"'
    assert dispatcher.command_out['reason_next'] == 'sunbased', '"reason_next" should be set to "sunbased"'

    # 5. force mode should be still active after static open, but next should be 'close'
    dispatcher.set_datetime_now('2020-01-01T08:45:00')
    controller.recalc()
    assert dispatcher.command_out['current'] is 'open', 'force mode set to "open", should be open now'
    assert dispatcher.command_out['next'] == 'close', '"next" should be set to "close"'
    assert dispatcher.command_out['reason_next'] == 'sunbased', '"reason_next" should be set to "sunbased"'
    assert dispatcher.command_out['next_time'] == datetime.fromisoformat('2020-01-01T17:07:00'),\
        '"next_time" should be set to "2020-01-01T17:07:00"'

    # 6. force mode timeout, static close should still be next
    dispatcher.set_datetime_now('2020-01-01T11:15:01')
    controller.recalc()
    assert dispatcher.command_out['current'] is None, 'force mode timeout. "current" should be None'
    assert dispatcher.command_out['next'] == 'close', '"next" should be set to "close"'
    assert dispatcher.command_out['reason_next'] == 'sunbased', '"reason_next" should be set to "static"'
    assert dispatcher.command_out['next_time'] == datetime.fromisoformat('2020-01-01T17:07:00'),\
        '"next_time" should be set to "2020-01-01T17:07:00"'

    # 7. force close
    dispatcher.set_datetime_now('2020-01-01T17:00:00')
    controller.set_force_operation('close', '2020-01-01T17:00:00')
    assert dispatcher.command_out['current'] is 'close', 'force mode set to "open", should be close now'
    assert dispatcher.command_out['next'] == 'close', '"next" should be set to "close"'
    assert dispatcher.command_out['reason_next'] == 'sunbased', '"reason_next" should be set to "static"'
    assert dispatcher.command_out['next_time'] == datetime.fromisoformat('2020-01-01T17:07:00'),\
        '"next_time" should be set to "2020-01-01T17:07:00"'

    # 8. advance after static close, force close still active
    dispatcher.set_datetime_now('2020-01-01T18:01:00')
    controller.recalc()
    assert dispatcher.command_out['current'] is 'close', 'force mode set to "open", should be close now'
    assert dispatcher.command_out['next'] == 'open', '"next" should be set to "open"'
    assert dispatcher.command_out['reason_next'] == 'sunbased', '"reason_next" should be set to "sunbased"'
    assert dispatcher.command_out['next_time'] == datetime.fromisoformat('2020-01-02T08:32:00'),\
        '"next_time" should be set to "2020-01-02T08:32:00"'

    # 9. set to auto
    controller.set_force_operation('auto', None)
    assert dispatcher.command_out['current'] is None, 'force mode set to "auto", "current" should be None'
    assert dispatcher.command_out['next'] == 'open', '"next" should be set to "open"'
    assert dispatcher.command_out['reason_next'] == 'sunbased', '"reason_next" should be set to "sunbased"'
    assert dispatcher.command_out['next_time'] == datetime.fromisoformat('2020-01-02T08:32:00'),\
        '"next_time" should be set to "2020-01-02T08:32:00"'


def test_sunbased_to_static():
    # expect that the completeness of the results is already tested
    dispatcher = Dispatcher('2020-01-01T00:00:00')
    controller = Controller()
    controller.init(controller_conf_1, dispatcher)
    controller.set_static_time('9:00', '18:00')
    controller.set_door_prio('sunbased', 'sunbased')
    controller.set_force_operation('auto', None)

    # 1. set to static
    door_times, door_times_converted =\
        timecontrol.recalc_door_times(time_control_1, datetime.fromisoformat('2020-01-01T09:00:00'), None, None)
    # door_times_converted =
    # {'sunrise_time': '08:17', 'sunset_time': '16:52', 'sunrise_open_time': '08:32', 'sunset_close_time': '17:07'}
    controller.set_sunbased_time(door_times_converted['sunrise_open_time'],
                                 door_times_converted['sunset_close_time'])
    controller.recalc(systemtime_synced=True)

    assert dispatcher.command_out['current'] is None, '"current" should be set to none'
    assert dispatcher.command_out['next'] == 'open', '"next" should be set to "open"'
    assert dispatcher.command_out['reason_next'] == 'sunbased', '"reason_next" should be set to "sunbased"'
    assert dispatcher.command_out['next_time'] == datetime.fromisoformat('2020-01-01T08:32:00'),\
        '"next_time" should be set to "2020-01-01T08:32:00"'

    # 2. open: change from sunbased to static
    controller.set_door_prio('static', 'sunbased')
    assert dispatcher.command_out['current'] is None, '"current" should be set to none'
    assert dispatcher.command_out['next'] == 'open', '"next" should be set to "open"'
    assert dispatcher.command_out['reason_next'] == 'static', '"reason_next" should be set to "static"'
    assert dispatcher.command_out['next_time'] == datetime.fromisoformat('2020-01-01T09:00:00'),\
        '"next_time" should be set to "2020-01-01T09:00:00"'

    # 3. change from static to sunbased when the time is over -> close should happen as next
    dispatcher.set_datetime_now('2020-01-01T08:45:00')
    controller.set_door_prio('sunbased', 'sunbased')
    assert dispatcher.command_out['current'] is None, '"current" should be set to none'
    assert dispatcher.command_out['next'] == 'close', '"next" should be set to "open"'
    assert dispatcher.command_out['reason_next'] == 'sunbased', '"reason_next" should be set to "sunbased"'
    assert dispatcher.command_out['next_time'] == datetime.fromisoformat('2020-01-01T17:07:00'),\
        '"next_time" should be set to "2020-01-01T17:07:00"'

    # 4. switch close from static to sunbased
    dispatcher.set_datetime_now('2020-01-01T17:00:00')
    controller.set_door_prio('static', 'static')
    assert dispatcher.command_out['current'] is None, '"current" should be set to none'
    assert dispatcher.command_out['next'] == 'close', '"next" should be set to "open"'
    assert dispatcher.command_out['reason_next'] == 'static', '"reason_next" should be set to "static"'
    assert dispatcher.command_out['next_time'] == datetime.fromisoformat('2020-01-01T18:00:00'),\
        '"next_time" should be set to "2020-01-01T18:00:00"'
