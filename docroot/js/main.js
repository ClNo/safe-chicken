import { MqttClient, CLIENT_ID } from "./mqtt_client.js";
import { InputConnector, SelectionConnector, TextOutConnector, TableOutConnector } from "./connectors.js";

const mqttHostname = '192.168.21.5';  // location.hostname
const mqttPort     = 9001;  // Number(location.port)

const TOPIC_DOOR_LIFESIGN = "safechicken/door_lifesign";
const TOPIC_COMMAND_OUT = "safechicken/command_out";
const TOPIC_LAST_COMMANDS = "safechicken/last_commands";
const TOPIC_DOOR_CLOSED_LOG = "safechicken/door_closed_log";

const TOPIC_SUN_TIMES   = "safechicken/sun_times";
const TOPIC_DOOR_SUN_TIMES_CONF   = "safechicken/door_sun_times_conf";
const TOPIC_DOOR_SUN_TIMES   = "safechicken/door_sun_times";
const TOPIC_DOOR_PRIO   = "safechicken/door_prio";
const TOPIC_STATIC_TIME   = "safechicken/static_time";
const TOPIC_FORCE_OPERATION   = "safechicken/force_operation";

Date.prototype.addHours = function(h) {
  this.setTime(this.getTime() + (h*60*60*1000));
  return this;
}

var onConnected = function onConnected(connected) {
  if(connected)  {
    $("#connected").html('Yes');
    $('#connected').removeClass('bg-danger').addClass('bg-success');
  }
  else {
    $("#connected").html('No');
    $('#connected').removeClass('bg-success').addClass('bg-danger');
    $('#txt-status-lifesign').removeClass('bg-danger').removeClass('bg-warning').removeClass('bg-success');
  }
}

var onDoorLifeSign = function onDoorLifeSign(selector, dataContent) {
  $(selector).removeClass('bg-danger').removeClass('bg-warning').removeClass('bg-success');
  if (!dataContent) {
    $(selector).html('not connected');
    $(selector).addClass('bg-danger');
  }
  else {
    var lastLifeSign = new Date(dataContent);
    console.log(lastLifeSign);
    var checkTime = new Date();
    checkTime.addHours(-0.1);

    $(selector).html(dataContent);
    if (lastLifeSign < checkTime) {
      $(selector).addClass('bg-warning');
    }
    else {
      $(selector).addClass('bg-success');
    }
  }
}


var onDoorSensor = function onDoorSensor(selector, dataContent) {
  $(selector).removeClass('bg-danger').removeClass('bg-warning').removeClass('bg-success');
  console.log('onDoorSensor', dataContent);
  if (!dataContent || (Object.keys(dataContent).length === 0)) {
    $(selector).html('no sensor');
  }
  else {
    // the first entry is the most recent door state
    $(selector).html(dataContent[0].state);
  }
}

$(document).ready(function() {

  // makes not much sense: $("#clientId").html(CLIENT_ID);

  // https://www.jonthornton.com/jquery-timepicker/
  // https://github.com/jonthornton/jquery-timepicker
  $('.bs-timepicker').timepicker({ 'timeFormat': 'H:i', 'step': 15, });

  // Web Socket MQTT Client Object.
  const client = new MqttClient(mqttHostname, mqttPort, CLIENT_ID, onConnected);

  let doorLifesign = new TextOutConnector(TOPIC_DOOR_LIFESIGN, ['last'], ['#txt-status-lifesign'], [onDoorLifeSign]);
  let doorSensor = new TextOutConnector(TOPIC_DOOR_CLOSED_LOG, null, ['#txt-door-sensor'], [onDoorSensor]);
  let nextTime = new TextOutConnector(TOPIC_COMMAND_OUT, ['next', 'next_time', 'reason_next'], ['#txt-status-next', '#txt-status-next-time', '#txt-status-reason-next']);
  let lastCommands = new TableOutConnector(TOPIC_LAST_COMMANDS, null, ['#table-last-commands']);
  let doorSensorLog = new TableOutConnector(TOPIC_DOOR_CLOSED_LOG, null, ['#table-door-sensor-log']);
  client.addConnector([doorLifesign, doorSensor, nextTime, lastCommands, doorSensorLog]);

  let doorOpenPrio = new SelectionConnector(TOPIC_DOOR_PRIO, 'open', 'input[name = "door-select-open-options"]', ['sunbased', 'static']);
  let doorClosePrio = new SelectionConnector(TOPIC_DOOR_PRIO, 'close', 'input[name = "door-select-close-options"]', ['sunbased', 'static']);
  let staticTimes = new InputConnector(TOPIC_STATIC_TIME, ['open', 'close'], ['#static-open-time', '#static-close-time'], []);
  let forceOperation = new SelectionConnector(TOPIC_FORCE_OPERATION, 'command', 'input[name = "force-operation-options"]', ['auto', 'open', 'close']);
  let forceTimeUntil = new TextOutConnector(TOPIC_FORCE_OPERATION, ['started_isodt'], ['#rad-txt-force-until-time']);
  client.addConnector([doorOpenPrio, doorClosePrio, staticTimes, forceOperation, forceTimeUntil]);

  let sunCalcTimes = new TextOutConnector(TOPIC_SUN_TIMES, ['sunrise_time', 'sunset_time'], ['#txt-sunrise-time', '#txt-sunset-time']);
  let minAfterSunrise = new InputConnector(TOPIC_DOOR_SUN_TIMES_CONF, ['min_after_sunrise'], ['#inp-min-after-sunrise'],  ['#txt-min-after-sunrise']);
  let minAfterSunset = new InputConnector(TOPIC_DOOR_SUN_TIMES_CONF, ['min_after_sunset'], ['#inp-min-after-sunset'],  ['#txt-min-after-sunset']);
  let doorSunCalcTimes = new TextOutConnector(TOPIC_DOOR_SUN_TIMES, ['door_sun_open_time', 'door_sun_close_time'], ['#txt-door-sun-open-time', '#txt-door-sun-close-time']);
  let sunDoorTimes = new TextOutConnector(TOPIC_SUN_TIMES, ['sunrise_open_time', 'sunrise_open_time', 'sunset_close_time', 'sunset_close_time'],
                         ['#txt-sunrise-open-time', '#rad-txt-open-sunrise-time', '#txt-sunset-close-time', '#rad-txt-close-sunset-time']);
  client.addConnector([sunCalcTimes, minAfterSunrise, minAfterSunset, doorSunCalcTimes, sunDoorTimes]);

  /*
  $("#force-operation-option2").click(function(event){
    var dt = new Date();
    console.log('clicked:', event.target.id, dt);
    const payload = {}
    payload['started_isodt'] = dt.toISOString();
    client.send(client, TOPIC_FORCE_OPERATION, payload);
  });
  $("#force-operation-option3").click(function(event){
    var dt = new Date();
    console.log('clicked:', event.target.id, dt);
    const payload = {}
    payload['started_isodt'] = dt.toISOString();
    client.send(client, TOPIC_FORCE_OPERATION, payload);
  });
  */

  client.connect();
});
