import swagger_ui_bundle
import connexion
import json
import datetime 
import requests
import time
from connexion import NoContent
import yaml
import logger
import logging.config
import uuid
from pykafka import KafkaClient
from threading import Thread
import os



MAX_EVENTS = 10
EVENT_FILE = 'events.json'

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

logger = logging.getLogger('basicLogger')

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

def ride(body):
    """ Receives ride data event"""

    trace = str(uuid.uuid4())
    body['traceID'] = trace
    print(body['traceID'])

    # logging to app.log
    logger.info('Received event ride event with a trace id of' + trace)

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

    msg = { "type": "heartrate",
            "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    
    # logging to app.log
    logger.info('Returned heartrate event response (Id: ' + trace + ') with status ' 
    + str(201))

    return NoContent, 201


def health():
    logger.info("Health Check returned 200")
    return 200


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)


hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
curr_retry = 0
while curr_retry < app_config["events"]["max_retry"]:
    try:
        logger.info(f"Trying to connect to Kafka, retry count: {curr_retry}")
        client = KafkaClient(hosts=hostname)
        topic = client.topics[str.encode(app_config["events"]["topic"])]
        producer = topic.get_sync_producer()
    except:
        logger.error("Connection Failed!")
        time.sleep(app_config["events"]["sleep"])
    curr_retry += 1


if __name__ == "__main__":
    app.run(port=8080)
