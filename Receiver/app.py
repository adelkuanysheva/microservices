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

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)


def ride(body):
    """ Receives ride data event"""

    trace = str(uuid.uuid4())
    body["traceID"] = trace

    # logging to app.log
    logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
    logger.info('Received event ride event with a trace id of' + trace)
    # logging to console
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
    logger.info('Received event ride event with a trace id of' + trace)

    res = requests.post(app_config['eventstore1']['url'], headers={
    'Content-Type': 'application/json'}, data=json.dumps(body))

    logger.info('Returned ride event response (Id: ' + trace + ') with status' 
    + str(res.status_code))

    # headers = {"content-type": "application/json"}
    # response = requests.post(app_config["eventstore1"].url,
    #                         json=body, headers=headers)

    # if response.status_code == 201:
    #     return NoContent, 201
    # if response.status_code == 400:
    #     return NoContent, 400

    return res.text, res.status_code

def heartrate(body):
    """ Receives heartrate data event"""

    headers = {"content-type": "application/json"}
    response = requests.post(app_config["eventstore2"].url,
                            json=body, headers=headers)

    if response.status_code == 201:
        return NoContent, 201
    if response.status_code == 400:
        return NoContent, 400


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    app.run(port=8080)