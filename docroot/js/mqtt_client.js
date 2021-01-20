const CLIENT_ID = String(Math.floor(Math.random() * 10e16))                            // (2)

// ---------------------------------------------------------------------------------------------------------------------
const merge = (...varArguments) => {

    // create a new object
    let target = {};

    // merge the object into the target object
    const merger = (obj) => {
        for (let prop in obj) {
            if (obj.hasOwnProperty(prop)) {
                target[prop] = obj[prop];
            }
        }
    };

    // iterate through all objects and merge them with target
    for (let i = 0; i < varArguments.length; i++) {
        merger(varArguments[i]);
    }

    return target;
};
// ---------------------------------------------------------------------------------------------------------------------

class DataHostClient {
    constructor(onConnected) {
        this.onConnected = onConnected;
        this.connectors = []
    }

    addConnector(connector) {
        if(connector.constructor.name  === 'Array') {
          this.connectors = this.connectors.concat(connector);
        }
        else {
          this.connectors.push(connector);
        }
    }

    getConnectorsByTopic(topic) {
        let connectorsList = [];
        for (let connector of this.connectors) {
            if (connector.getTopic() == topic) {
                connectorsList.push(connector);
            }
        }
        return connectorsList;
    }

    dataHostConnected(connected) {
        this.onConnected(connected);
        for (let connector of this.connectors) {
            connector.dataHostConnected(connected);
        }
    }

    initTransfer() {
        for (let connector of this.connectors) {
            connector.setSenderFunc(this, this.send);
        }
    }

    initWebSide() {
        for (let connector of this.connectors) {
            connector.initWebSide();
        }
    }
}


class MqttClient extends DataHostClient {
    constructor(hostname, port, clientID, onConnected) {
        super(onConnected);
        this.hostname = hostname;
        this.port = port;
        this.clientID = clientID;
        this.client = new Paho.MQTT.Client(this.hostname, this.port, this.clientID);

        this.incomingTree = {};
    }

    connect() {
        super.initWebSide();

        const thisClass = this;
        this.client.connect({
            onSuccess: function(data) { thisClass.onConnectionSuccess(data); },
            reconnect: true  // <------------ true/false?
        });

        this.client.onConnectionLost = function(data) { thisClass.onConnectionLost(data); }
        this.client.onMessageArrived = function(message) { thisClass.onMessageArrived(message); }
        super.initTransfer();
    }

    // Callback when client has connected to Broker.
    onConnectionSuccess(data) {
      console.log('Connected to MQTT Broker', this.hostname, 'on port', this.port);
      super.dataHostConnected(true);

      for (let connector of this.connectors) {
        this.client.subscribe(connector.getTopic());
      }
    };


    // Callback when client looses it's connection to Broker.
    onConnectionLost(data) {
      if (data.errorCode !== 0) {
        console.log("Disconnected from Connected to MQTT Broker with error " + data.errorMessage);
      } else {
        console.log("Disconnected from MQTT Broker");
      }

      super.dataHostConnected(false);
    };

    // Callback when a new message arrives at a subscribed topic.
    onMessageArrived(message) {                         // (9)

      console.log("onMessageArrived:" + message.payloadString + " for topic " + message.destinationName);

      var data = JSON.parse(message.payloadString);
      this.incomingTree[message.destinationName] = merge(this.incomingTree[message.destinationName], data);

      const connectorsList = super.getConnectorsByTopic(message.destinationName);
      for (let connector of connectorsList) {
        if (connector) {
          console.log('connector found:', connector.getSelectors(), ' keys: ', connector.getTopicFullStr());
          connector.valueArrived(data);
        }
      }
    }

    send(senderObj, topic, payload) {
      // Note: if it's a complex object we need to send, we have to send to whole object! Otherwise only one part of the
      // expected object is set and the rest of it is missing but expected which leads to errors in the client.
      // So we have to merge the payload to the incoming tree (or at least the topic) and everything is fine.
      var mergedTopicMessage = merge(senderObj.incomingTree[topic], payload);

      var message = new Paho.MQTT.Message(JSON.stringify(mergedTopicMessage));
      message.destinationName = topic;
      message.qos = 2;
      message.retained = true;

      console.log('sending message for ', topic, ':', mergedTopicMessage);
      senderObj.client.send(message);
    }
}


export { MqttClient, CLIENT_ID };
