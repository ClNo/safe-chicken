from datetime import datetime, timedelta, time


class Controller:
    def __init__(self):
        self.config = None
        self.callback = None
        self.open_prio = None
        self.close_prio = None
        self.static_time_open = None
        self.static_time_close = None
        self.force_command = None
        self.force_time = None
        self.sun_time_open = None
        self.sun_time_close = None
        self.systemtime_synced = False  # this specifies whether the system date is valid or not
        self.systemtime_err_reported = False

        self.command_out = {'current': None, 'reason': None,
                            'open_next_time': None, 'open_next_reason': None,
                            'close_next_time': None, 'close_next_reason': None,
                            'next': None, 'next_time': None, 'reason_next': None}

    def init(self, config_dict, callback):
        self.config = config_dict
        self.callback = callback

    def set_door_prio(self, open_prio, close_prio):
        self.open_prio = open_prio
        self.close_prio = close_prio
        self._recalc_next_action()

    def set_sunbased_time(self, time_open, time_close):
        self.sun_time_open = time_open
        self.sun_time_close = time_close
        self._recalc_next_action()

    def set_static_time(self, time_open, time_close):
        self.static_time_open = time_open
        self.static_time_close = time_close
        self._recalc_next_action()

    def set_force_operation(self, force_command, force_time):
        self.force_command = force_command
        if force_time:
            iso_cut = force_time
            if force_time[-1] == 'Z':
                # this is unknown to Python :(
                iso_cut = force_time[:-1]
            self.force_time = datetime.fromisoformat(iso_cut)  # hack: cut the last 'Z' char; not supported by Python!? <---
        else:
            self.force_time = None
        self._recalc_next_action()

    def recalc(self, systemtime_synced=None):
        if (systemtime_synced is not None) and systemtime_synced:
            self.systemtime_synced = systemtime_synced
        self._recalc_next_action()

    def _recalc_next_action(self):
        self.command_out = {'current': None, 'reason': None,
                            'open_next_time': None, 'open_next_reason': None,
                            'close_next_time': None, 'close_next_reason': None,
                            'next': None, 'next_time': None, 'reason_next': None}

        if not self.systemtime_synced:
            if not self.systemtime_err_reported:
                self.callback.report_err(100, 'system date not set, check time synchronisation')
                self.callback.command_changed(self.command_out)
                self.systemtime_err_reported = True
            return
        else:
            self.systemtime_err_reported = False

        try:
            # --- handle force operation
            if self.force_command and self.force_time:
                force_time_expire = self.force_time + timedelta(minutes=self.config['force_time_expire_minutes'])
                if (self.force_command == 'open') and (self.callback.get_datetime_now() < force_time_expire):
                    self.command_out['current'] = 'open'
                    self.command_out['reason'] = 'force'
                elif (self.force_command == 'close') and (self.callback.get_datetime_now() < force_time_expire):
                    self.command_out['current'] = 'close'
                    self.command_out['reason'] = 'force'

                if self.callback.get_datetime_now() >= force_time_expire:
                    # force expiry time is over, clear current command for now
                    self.command_out['current'] = None
                    self.command_out['reason'] = 'force_expire'
                    if self.force_command != 'auto':
                        self.callback.notify_force_expired()

            if self.force_time is None:
                if self.force_command != 'auto':
                    self.callback.notify_force_expired()

            # --- 1. calc OPEN time according to the prio
            if (self.open_prio == 'sunbased') and self.sun_time_open:
                sun_open_next = self._calc_next_datetime(self.sun_time_open)
                self.command_out['open_next_time'] = sun_open_next
                self.command_out['open_next_reason'] = 'sunbased'
            elif (self.open_prio == 'static') and self.static_time_open:
                static_open_next = self._calc_next_datetime(self.static_time_open)
                self.command_out['open_next_time'] = static_open_next
                self.command_out['open_next_reason'] = 'static'
            elif self.sun_time_open:
                # this should never occur - only if prio set to 'static' but no time is given
                sun_open_next = self._calc_next_datetime(self.sun_time_open)
                self.command_out['open_next_time'] = sun_open_next
                self.command_out['open_next_reason'] = 'sunbased-no-static-time'

            # --- 2. calc CLOSE time according to the prio
            if (self.close_prio == 'sunbased') and self.sun_time_close:
                sun_close_next = self._calc_next_datetime(self.sun_time_close)
                self.command_out['close_next_time'] = sun_close_next
                self.command_out['close_next_reason'] = 'sunbased'
            elif (self.close_prio == 'static') and self.static_time_close:
                static_close_next = self._calc_next_datetime(self.static_time_close)
                self.command_out['close_next_time'] = static_close_next
                self.command_out['close_next_reason'] = 'static'
            elif self.sun_time_close:
                # this should never occur - only if prio set to 'static' but no time is given
                sun_close_next = self._calc_next_datetime(self.sun_time_close)
                self.command_out['close_next_time'] = sun_close_next
                self.command_out['close_next_reason'] = 'sunbased-no-static-time'

            # --- 3. which action comes first? open or close?
            if self.command_out['open_next_time'] and self.command_out['close_next_time']:
                if self.command_out['open_next_time'] < self.command_out['close_next_time']:
                    self.command_out['next'] = 'open'
                    self.command_out['next_time'] = self.command_out['open_next_time']
                    self.command_out['reason_next'] = self.command_out['open_next_reason']
                else:
                    self.command_out['next'] = 'close'
                    self.command_out['next_time'] = self.command_out['close_next_time']
                    self.command_out['reason_next'] = self.command_out['close_next_reason']
            # else: do nothing (expected forced mode is set in 'current')

        except ValueError as e:  # Exception as e:
            self.callback.report_err(101, 'Not all calculation data received yet: {0}'.format(str(e)))
            return

        self.callback.clear_err()
        self.callback.command_changed(self.command_out)

    def _calc_next_datetime(self, time_str):
        if not time_str:
            return None
        datetime_next = datetime.combine(self.callback.get_datetime_now(), time(int(time_str.split(':')[0]), int(time_str.split(':')[1])))
        if datetime_next < self.callback.get_datetime_now():
            datetime_next += timedelta(days=1)
        return datetime_next
