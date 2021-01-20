import argparse
import datetime
import json
import time
import subprocess
from copy import deepcopy

from safechicken import timecontrol, mqttclient, iocontrol
from safechicken import controller


config_dict = {}


class TimeSyncFlag:
    def __init__(self):
        self.systemtime_synced = False
        self.timesync_err_reported = False

    def update_timesync_flag(self):
        if self.systemtime_synced:
            # do nothing if it has been synced once
            return

        try:
            command = ['timedatectl', '-p', 'NTPSynchronized', 'show']
            res = subprocess.check_output(command)

            ntp_line = [line for line in res.decode("utf-8").splitlines() if 'Synchronized' in line]
            if '=yes' in ntp_line:
                print('timesync working, system clock set: {0}'.format(datetime.datetime.now().isoformat()))
                self.systemtime_synced = True
                return

        except Exception as e:
            if not self.timesync_err_reported:
                print('Error executing timesync query command: {0}'.format(e))
            self.timesync_err_reported = True

        # self.timesync_err_reported = False -> try old style
        try:
            command = ['timedatectl', 'status']
            print('trying old style time sync command... {0}'.format(command))
            res = subprocess.check_output(command)

            ntp_line = [line for line in res.decode("utf-8").splitlines() if 'synchronized' in line]
            if any('yes' in s for s in ntp_line):
                print('timesync working, system clock set: {0}'.format(datetime.datetime.now().isoformat()))
                self.systemtime_synced = True
                return

        except Exception as e:
            if not self.timesync_err_reported:
                print('Error executing timesync query command: {0}'.format(e))
            self.timesync_err_reported = True


    def is_systemtime_synced(self):
        return self.systemtime_synced


class Dispatcher:
    def __init__(self, mqtt_client: mqttclient.MqttClient, contr: controller.Controller, io: iocontrol.IoController,
                 timesync: TimeSyncFlag):
        self.mqtt_client: mqttclient.MqttClient = mqtt_client
        self.controller: controller.Controller = contr
        self.io: iocontrol.IoController = io
        self.timesync: TimeSyncFlag = timesync

        self.last_command_bak = None

    def update_status(self):
        systemtime_synced = self.timesync.is_systemtime_synced()
        is_mqtt_connected = self.mqtt_client.is_connected()
        self.io.update_status_out(systemtime_synced, is_mqtt_connected)

    # ---------- controller callback methods ----------
    def notify_force_expired(self):
        global config_dict
        self.mqtt_client.publish(config_dict['topic_conf']['force_operation'], {'command': 'auto', 'started_isodt': None})

    def report_err(self, code, err_str):
        print('error {0}: {1}'.format(code, err_str))

    def clear_err(self):
        pass

    def command_changed(self, command_out):
        if command_out != self.last_command_bak:
            self.last_command_bak = deepcopy(command_out)
            print('Next action is: {0}'.format(command_out))
            self.io.update_commands(command_out)
            self.update_status()

            next_time_conv = None
            if command_out['next_time']:
                next_time_conv = command_out['next_time'].strftime('%H:%M')

            command_out_pub = {
                'current': command_out['current'], 'reason': command_out['reason'],
                'next': command_out['next'],
                'next_time': next_time_conv,
                'reason_next': command_out['reason_next']
            }
            self.mqtt_client.publish(config_dict['topic_conf']['command_out'], command_out_pub)
        # else: no change of outputs

    def get_datetime_now(self):
        # callback method as it is mocked for testing
        return datetime.datetime.now()
    # ---------- controller callback methods ----------

    # ---------- incoming event methods ----------
    def on_sun_times_conf(self, topic, content_dict):
        print('message arrived, topic {0}: {1}'.format(topic, content_dict))

        global config_dict

        try:
            min_after_sunrise = int(content_dict['min_after_sunrise'])
            min_after_sunset = int(content_dict['min_after_sunset'])
            door_times, door_times_converted = timecontrol.recalc_door_times(config_dict['time_control'], datetime.date.today(), min_after_sunrise, min_after_sunset)
            self.mqtt_client.publish(config_dict['topic_conf']['sun_times'], door_times_converted)
        except KeyError as e:
            print('Unexpected/missing MQTT content in {0}: {1}'.format(topic, e))

    def on_door_prio(self, topic, content_dict):
        print('message arrived, topic {0}: {1}'.format(topic, content_dict))
        self.controller.set_door_prio(content_dict['open'], content_dict['close'])

    def on_static_time(self, topic, content_dict):
        print('message arrived, topic {0}: {1}'.format(topic, content_dict))
        try:
            self.controller.set_static_time(content_dict['open'], content_dict['close'])
        except KeyError as e:
            print('Unexpected/missing MQTT content in {0}: {1}'.format(topic, e))

    def on_force_operation(self, topic, content_dict):
        print('message arrived, topic {0}: {1}'.format(topic, content_dict))
        if 'started_isodt' in content_dict:
            self.controller.set_force_operation(content_dict['command'], content_dict['started_isodt'])
        else:
            self.controller.set_force_operation(content_dict['command'], None)
    # ---------- incoming event methods ----------


def main():
    parser = argparse.ArgumentParser(description='Door control for chicken - using MQTT for diagnostics')
    parser.add_argument('config_file', help='JSON configuration file', type=argparse.FileType('r'))
    args = parser.parse_args()

    global config_dict
    config_dict = json.load(args.config_file)

    contr: controller.Controller = controller.Controller()
    io: iocontrol.IoController = iocontrol.IoController(config_dict['io'])
    timesync: TimeSyncFlag = TimeSyncFlag()
    timesync.update_timesync_flag()

    # mqttclient.test_connection(config_dict['mqtt_client'])
    mqtt_client: mqttclient.MqttClient = mqttclient.MqttClient(config_dict['mqtt_client'], config_dict['topic_conf'])
    dispatcher: Dispatcher = Dispatcher(mqtt_client, contr, io, timesync)
    contr.init(config_dict['controller'], dispatcher)

    last_calc_date = datetime.date.today()
    door_times, door_times_converted = timecontrol.recalc_door_times(config_dict['time_control'], last_calc_date, None, None)
    contr.set_sunbased_time(door_times_converted['sunrise_open_time'], door_times_converted['sunset_close_time'])
    print('initially calculated sunrise and sunset time for {0}: {1}'.format(last_calc_date.isoformat(), door_times_converted))

    topic_list = [
        (config_dict['topic_conf']['door_sun_times_conf'], dispatcher.on_sun_times_conf),
        (config_dict['topic_conf']['door_prio'], dispatcher.on_door_prio),
        (config_dict['topic_conf']['static_time'], dispatcher.on_static_time),
        (config_dict['topic_conf']['force_operation'], dispatcher.on_force_operation)
    ]
    mqtt_client.connect_subscribe(topic_list)
    mqtt_client.publish(config_dict['topic_conf']['sun_times'], door_times_converted)

    last_command_list = None
    door_closed_log = None

    while True:
        # sleep time but note: MQTT client is listening and always active
        time.sleep(60)
        print('.')

        # periodical checks
        # 1. check MQTT connection
        if not mqtt_client.is_connected():
            mqtt_client.connect_subscribe(topic_list)
            mqtt_client.publish(config_dict['topic_conf']['sun_times'], door_times_converted)

        # 2. check if systemtime synced
        timesync.update_timesync_flag()

        # 3. update status LEDs
        dispatcher.update_status()

        # TODO <------- first execute the last command again to not skip the automatic time and directly jump to the next!
        io.execute_pending_command()

        # 4. recalc today's sunrise and sunset times
        if timesync.is_systemtime_synced():
            if last_calc_date != datetime.date.today():
                last_calc_date = datetime.date.today()
                door_times, door_times_converted = timecontrol.recalc_door_times(config_dict['time_control'],
                                                                                 last_calc_date, None, None)
                contr.set_sunbased_time(door_times_converted['sunrise_open_time'],
                                        door_times_converted['sunset_close_time'])
                print('recalculated sunrise and sunset time for {0}: {1}'.format(last_calc_date.isoformat(), door_times_converted))

        # 5. recalc open/close state -> this will automatically set the IOs via the dispatcher
        contr.recalc(timesync.is_systemtime_synced())

        # 6. publish last commands
        if last_command_list != io.get_last_command_list():
            last_command_list = io.get_last_command_list()
            mqtt_client.publish(config_dict['topic_conf']['last_commands'], last_command_list)

        # 7. publish last door states (digital input)
        if door_closed_log != io.get_door_state_log():
            door_closed_log = io.get_door_state_log()
            mqtt_client.publish(config_dict['topic_conf']['door_closed_log'], door_closed_log)

        # 8. send life sign
        mqtt_client.publish_volatile(config_dict['topic_conf']['door_lifesign'], {'last': datetime.datetime.now().isoformat(timespec='seconds')})

    mqtt_client.disconnect()


if __name__ == '__main__':
    main()

