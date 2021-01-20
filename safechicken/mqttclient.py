import functools
import json

import paho.mqtt.client as mqtt
import time


def test_connection(mqtt_config):
    print(mqtt_config)

    def on_message(client, userdata, message):
        print("received message: ", str(message.payload.decode("utf-8")))

    mqtt_broker = mqtt_config['broker_hostname']

    client = mqtt.Client(mqtt_config['client_name'])
    client.connect(mqtt_broker)

    #  client.publish("TEMPERATURE", randNumber)

    client.loop_start()

    client.subscribe("test1/topic1")
    client.on_message = on_message

    time.sleep(60)
    client.loop_stop()


def _on_mqtt_message(mqtt_client, paho_client, userdata, message):
    print('received message {0}: {1}'.format(message.topic, str(message.payload.decode("utf-8"))))
    topic_func = mqtt_client.get_topic_func(message.topic)
    if topic_func:
        topic_func(message.topic, json.loads(message.payload.decode("utf-8")))


class MqttClient:
    def __init__(self, mqtt_config, topic_config):
        self.mqtt_config = mqtt_config
        self.topic_config = topic_config
        self.client = mqtt.Client(mqtt_config['client_name'])
        self.topic_list = []

    def connect_subscribe(self, topic_list):
        try:
            self.client.connect(self.mqtt_config['broker_hostname'])
            self.client.on_message = functools.partial(_on_mqtt_message, self)
            self.client.loop_start()
            print('MQTT connected to {0}'.format(self.mqtt_config['broker_hostname']))

            self.topic_list = topic_list

            for topic_elem in topic_list:
                self.client.subscribe(topic_elem[0])
        except Exception as e:
            print('Error on MQTT connection (retry later): {0}'.format(e))

    def disconnect(self):
        self.client.loop_stop()

    def publish(self, topic, content_dict):
        self.client.publish(topic=topic, payload=json.dumps(content_dict), retain=True)

    def publish_volatile(self, topic, content_dict):
        self.client.publish(topic=topic, payload=json.dumps(content_dict), retain=False)

    def get_topic_func(self, topic_name):
        for topic_elem in self.topic_list:
            if topic_elem[0] == topic_name:
                return topic_elem[1]
        return None

    def is_connected(self):
        return self.client.is_connected()
