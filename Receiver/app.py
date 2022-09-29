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


MAX_EVENTS = 10
EVENT_FILE = 'events.json'

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('./log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)


def ride(body):
    """ Receives ride data event"""

    trace = str(uuid.uuid4())
    body["traceID"] = trace

    # logging to app.log
    logger.info('Received event ride event with a trace id of' + trace)

    res = requests.post(app_config['eventstore1']['url'], headers={
    'Content-Type': 'application/json'}, data=json.dumps(body))

    # logging to app.log
    logger.info('Returned ride event response (Id: ' + trace + ') with status' 
    + str(res.status_code))

    return res.text, res.status_code

def heartrate(body):
    """ Receives heartrate data event"""

    trace = str(uuid.uuid4())
    body["traceID"] = trace

    # logging to app.log
    logger.info('Received event heartrate event with a trace id of' + trace)

    res = requests.post(app_config['eventstore2']['url'], headers={
    'Content-Type': 'application/json'}, data=json.dumps(body))

    # logging to app.log
    logger.info('Returned heartrate event response (Id: ' + trace + ') with status' 
    + str(res.status_code))

    return res.text, res.status_code


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    app.run(port=8080)