class QueryStateExtension {
  constructor(zigbee, mqtt, state, publishEntityState, eventBus, settings, logger) {
    this.state = state;
    this.zigbee = zigbee;
    this.logger = logger;
    this.mqttBaseTopic = settings.get().mqtt.base_topic;
    this.eventBus = eventBus;
    this.mqtt = mqtt;
  }

  start() {
    const mqttHandler = (topic, message) => {
      if (topic.startsWith(`${this.mqttBaseTopic}/`) && topic.endsWith('/get')) {
        const deviceId = topic.slice(this.mqttBaseTopic.length + 1, -4);
        const requestedKey = Object.keys(JSON.parse(message))[0];
        const queriedDeviceState = this.state.state[deviceId];
        console.log('Parsed message:', { topic, deviceId });

        if (queriedDeviceState) {
          const batteryExpose = queriedDeviceState['battery'];
          if (batteryExpose) {
            const response = { [requestedKey]: batteryExpose };
            this.mqtt.publish(`${deviceId}`, JSON.stringify(response));
          } else {
            this.logger.error(`Device with ID ${deviceId} does not have a battery expose.`);
          }
        } else {
          this.logger.error(`Device with ID ${deviceId} not found.`);
        }
      }
    };

    this.eventBus.onMQTTMessagePublished(this, data => mqttHandler(data.topic, data.payload), this.constructor.name);
    this.eventBus.onMQTTMessage(this, data => mqttHandler(data.topic, data.message), this.constructor.name);
  }

  async stop() {
    this.eventBus.removeListeners(this.constructor.name);
  }
}

module.exports = QueryStateExtension;
