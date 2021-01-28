import copy
import functools
import json

import paho.mqtt.client as mqtt
import time
import logging


def test_connection(mqtt_config):
    logging.info(mqtt_config)

    def on_message(client, userdata, message):
        logging.info("received message: ", str(message.payload.decode("utf-8")))

    mqtt_broker = mqtt_config['broker_hostname']

    client = mqtt.Client(mqtt_config['client_name'])
    client.connect(mqtt_broker)

    #  client.publish("TEMPERATURE", randNumber)

    client.loop_start()

    client.subscribe("test1/topic1")
    client.on_message = on_message

    time.sleep(60)
    client.loop_stop()


class MqttClient:
    def __init__(self, mqtt_config, topic_config):
        self.mqtt_config = mqtt_config
        self.topic_config = topic_config
        self.client = mqtt.Client(mqtt_config['client_name'])
        self.host = self.mqtt_config['broker_hostname']
        self.topic_list = []
        self.published_backup = {}

    def connect_subscribe(self, topic_list):
        try:
            self.topic_list = topic_list
            self.client.on_connect = functools.partial(_on_connect, self)
            self.client.on_message = functools.partial(_on_mqtt_message, self)
            self.client.connect(self.host)
            self.client.loop_start()

        except Exception as e:
            logging.warning('Error on MQTT connection (retry later): {0} (topic list size: {1})'.
                            format(e, len(topic_list)))

    def subscribe_now(self):
        try:
            for topic_elem in self.topic_list:
                topic_name = topic_elem[0]
                logging.info('Subscribe for topic {0}'.format(topic_name))
                self.client.subscribe(topic_name)

            # re-publish everything again. this is needed if an IO changes its state while the MQTT client is disconnected
            for topic_elem in self.published_backup:
                self.client.publish(topic=topic_elem, payload=self.published_backup[topic_elem], retain=True)

        except Exception as e:
            logging.warning('Error on MQTT connection (retry later): {0} (topic list size: {1})'.
                            format(e, len(self.topic_list)))

    def disconnect(self):
        self.client.loop_stop()

    def publish(self, topic, content_dict):
        self.published_backup[topic] = json.dumps(content_dict)
        self.client.publish(topic=topic, payload=self.published_backup[topic], retain=True)

    def publish_volatile(self, topic, content_dict):
        self.client.publish(topic=topic, payload=json.dumps(content_dict), retain=False)

    def get_topic_func(self, topic_name):
        for topic_elem in self.topic_list:
            if topic_elem[0] == topic_name:
                return topic_elem[1]
        return None

    def is_connected(self):
        return self.client.is_connected()


def _on_mqtt_message(mqtt_client: MqttClient, paho_client, userdata, message):
    logging.info('received message {0}: {1}'.format(message.topic, str(message.payload.decode("utf-8"))))
    topic_func = mqtt_client.get_topic_func(message.topic)
    if topic_func:
        topic_func(message.topic, json.loads(message.payload.decode("utf-8")))


def _on_connect(mqtt_client: MqttClient, client, userdata, flags, rc):
    if rc == 0:
        logging.info('MQTT connected to {0} (topic list size: {1})'.
                     format(mqtt_client.host, len(mqtt_client.topic_list)))
        mqtt_client.subscribe_now()

    else:
        logging.info('Failed to connect to {0}, return code {1}'.format(mqtt_client.host, rc))
