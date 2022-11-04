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


def ride(index):
    """ Get ride Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    logger.info("Retrieving ride at index %d" % index)
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if index - 1 <= 0:
                logger.info(msg)
                return msg
            if counter == index - 1:
                logger.info(msg)
                return msg, 200
            if counter <= index - 1:
                if msg['type'] == 'ride':
                    counter += 1
    except:
        logger.error("No more messages found")
        logger.error("Could not find ride at index %d" % index)

    return { "message": "Not Found"}, 404

def heartrate(index):
    """ Get heartrate Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    logger.info("Retrieving ride at index %d" % index)
    try:
        counter = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if index - 1 <= 0:
                logger.info(msg)
                return msg
            if counter == index - 1:
                logger.info(msg)
                return msg, 200
            if counter <= index - 1:
                if msg['type'] == 'heartrate':
                    counter += 1
    except:
        logger.error("No more messages found")
        logger.error("Could not find ride at index %d" % index)

    return { "message": "Not Found"}, 404


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    app.run(port=8200)