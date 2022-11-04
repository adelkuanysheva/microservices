import swagger_ui_bundle
import connexion
import json
import datetime 
import requests
from connexion import NoContent
import yaml
import logger
import logging.config
import uuid
from pykafka import KafkaClient


MAX_EVENTS = 10
EVENT_FILE = 'events.json'

logger = logging.getLogger('basicLogger')

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)


def ride(body):
    """ Receives ride data event"""

    trace = str(uuid.uuid4())
    body['traceID'] = trace
    print(body['traceID'])

    # logging to app.log
    logger.info('Received event ride event with a trace id of' + trace)

    # res = requests.post(app_config['eventstore1']['url'], headers={
    # 'Content-Type': 'application/json'}, data=json.dumps(body))
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    producer = topic.get_sync_producer()
    msg = { "type": "ride",
            "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    # logging to app.log
    logger.info(msg)
    logger.info('Returned ride event response (Id: ' + trace + ') with status ' 
    + str(201))

    return NoContent, 201


def heartrate(body):
    """ Receives heartrate data event"""

    trace = str(uuid.uuid4())
    body["traceID"] = trace

    # logging to app.log
    logger.info('Received event heartrate event with a trace id of' + trace)

    # res = requests.post(app_config['eventstore2']['url'], headers={
    # 'Content-Type': 'application/json'}, data=json.dumps(body))
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)    
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    producer = topic.get_sync_producer()
    msg = { "type": "heartrate",
            "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    
    # logging to app.log
    logger.info('Returned heartrate event response (Id: ' + trace + ') with status ' 
    + str(201))

    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    app.run(port=8080)
