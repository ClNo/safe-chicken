# https://gpiozero.readthedocs.io/en/stable/
import copy
from datetime import datetime

from gpiozero import LED, DigitalOutputDevice, DigitalInputDevice, Device
from gpiozero.pins.mock import MockFactory
import threading
import logging

import os
if not os.uname()[4].startswith("arm"):
    Device.pin_factory = MockFactory()


class IoController:
    def __init__(self, config_dict):
        self.config_dict = config_dict

        self.out_ready_led = LED(self.config_dict['out_ready_led'])
        self.out_network_status_led = LED(self.config_dict['out_network_status_led'])
        self.out_open_command = DigitalOutputDevice(self.config_dict['out_open_command'])
        self.out_close_command = DigitalOutputDevice(self.config_dict['out_close_command'])

        self.in_door_closed = DigitalInputDevice(self.config_dict['in_door_closed']['pin'],
                                                 active_state=self.config_dict['in_door_closed']['active_state'],
                                                 pull_up=None,
                                                 bounce_time=1.0)
        self.in_door_closed.when_activated = self.on_door_not_closed
        self.in_door_closed.when_deactivated = self.on_door_closed

        self.systemtime_synced = False
        self.clear_timer = None
        self.last_command_out = None
        self.last_command_list = []
        self.door_closed_log = []

    def update_commands(self, command_out):
        if command_out['current'] == 'open':
            self._check_and_open('force')
        elif command_out['current'] == 'close':
            self._check_and_close('force')
        self.last_command_out = copy.deepcopy(command_out)

    def execute_pending_command(self):
        if (not self.last_command_out) or ('next_time' not in self.last_command_out) or (not self.last_command_out['next_time']):
            # no time at all -> do nothing
            return

        if not self._time_passed(self.last_command_out['next_time']):
            # waiting time not passed yet
            return

        logging.info('Waiting time {0} passed'.format(self.last_command_out['next_time']))

        if self.last_command_out['current'] is not None:
            # force operation already done in update_commands()
            logging.info('Skipping automatic action because of force command!')
            return

        # there is no force operation so check if we need to execute the next command
        # note this command is only given if the timesync worked, so now() will be correct
        if (self.last_command_out['next'] == 'open') and self._time_passed(self.last_command_out['next_time']):
            self._check_and_open(self.last_command_out['reason_next'])
        elif (self.last_command_out['next'] == 'close') and self._time_passed(self.last_command_out['next_time']):
            self._check_and_close(self.last_command_out['reason_next'])
        # else: only appears if time not set; do nothing
        logging.info('Automatic action for {0} done'.format(self.last_command_out['next_time']))

    def update_status_out(self, systemtime_synced, is_mqtt_connected):
        if systemtime_synced:
            self.out_ready_led.on()
            self.systemtime_synced = systemtime_synced
        else:
            self.out_ready_led.off()

        if is_mqtt_connected:
            self.out_network_status_led.on()
        else:
            self.out_network_status_led.off()

    def get_last_command_list(self):
        return copy.deepcopy(self.last_command_list)

    def get_door_state_log(self):
        return copy.deepcopy(self.door_closed_log)

    def on_door_closed(self):
        logging.info('input: door closed')
        self.door_closed_log.insert(0, {'state': 'close', 'datetime': datetime.now().isoformat(timespec='minutes')})
        if len(self.door_closed_log) > 10:
            del self.door_closed_log[-1]

    def on_door_not_closed(self):
        logging.info('input: door NOT closed/opening/open')
        self.door_closed_log.insert(0, {'state': 'open', 'datetime': datetime.now().isoformat(timespec='minutes')})
        if len(self.door_closed_log) > 10:
            del self.door_closed_log[-1]

    def _check_and_open(self, reason):
        self.out_close_command.off()
        self.out_open_command.on()
        logging.info('io: open command, reason {0}'.format(reason))
        self._start_clear_timer()

        self.last_command_list.insert(0, {'command': 'open', 'datetime': datetime.now().isoformat(timespec='minutes'), 'reason': reason})
        if len(self.last_command_list) > 5:
            del self.last_command_list[-1]

    def _check_and_close(self, reason):
        self.out_open_command.off()
        self.out_close_command.on()
        logging.info('io: close command, reason {0}'.format(reason))
        self._start_clear_timer()

        self.last_command_list.insert(0, {'command': 'close', 'datetime': datetime.now().isoformat(timespec='minutes'), 'reason': reason})
        if len(self.last_command_list) > 5:
            del self.last_command_list[-1]

    def _start_clear_timer(self):
        if self.clear_timer:
            if self.clear_timer.is_alive():
                self.clear_timer.cancel()
                self.clear_timer.join()
        self.clear_timer = threading.Timer(self.config_dict['command_out_pulse_time_s'], self._clear_command_out)
        self.clear_timer.start()

    def _clear_command_out(self):
        logging.info('io: clear command out')
        self.out_open_command.off()
        self.out_close_command.off()

    def _time_passed(self, check_time):
        if (not self.systemtime_synced) or (not check_time):
            # do nothing of time is not correct
            return False

        return check_time < datetime.now()


# https://gpiozero.readthedocs.io/en/stable/api_output.html#base-classes

# class gpiozero.DigitalOutputDevice(pin, *, active_high=True, initial_value=False, pin_factory=None)
