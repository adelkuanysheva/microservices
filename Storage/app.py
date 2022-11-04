import swagger_ui_bundle
import connexion
from connexion import NoContent
import json
import datetime 
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from ride import Ride
from heartrate import HeartRate
import mysql.connector
import pymysql 
import yaml
import logging
import logger
import logging.config
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread


logger = logging.getLogger('basicLogger')

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

MAX_EVENTS = 10
EVENT_FILE = 'events.json'
DB_ENGINE = create_engine('mysql+pymysql://{}:{}@{}:{}/{}'
        .format(app_config['datastore']["user"], 
                app_config['datastore']["password"], 
                app_config['datastore']["hostname"], 
                app_config['datastore']["port"],
                app_config['datastore']["db"]))
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def storeRide(payload):

    trace_id = payload['traceID']
    session = DB_SESSION()
    bp = Ride(payload['user_id'], 
                    payload['movie'],
                    payload['timestamp'],
                    payload['avg_speed'],
                    payload['avg_power'],
                    payload['distance'], 
                    payload['traceID'])
    session.add(bp)
    session.commit()
    session.close()
    logger.info(f'Stored event rideEvent with a trace id of {trace_id}')
    
    logger.info('Connecting to DB. Hostname: {}, Port: {}'.format(app_config['datastore']["hostname"], app_config['datastore']["port"]))
    return "Saved ride reading to db"


def get_ride(timestamp):
    """ Gets new ride readings after the timestamp """
    
    logger.info('Connecting to DB. Hostname: {}, Port: {}'.format(app_config['datastore']["hostname"], app_config['datastore']["port"]))
    session = DB_SESSION()
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    readings = session.query(Ride).filter(Ride.date_created >= timestamp_datetime)
    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())

    session.close()

    logger.info("Query for ride data readings after %s returns %d results" % (timestamp, len(results_list)))
    return results_list, 200

    
def storeHeartrate(payload):
    trace_id = payload['traceID']
    session = DB_SESSION()
    bp = HeartRate(payload['user_id'],
                    payload['device_id'],
                    payload['heart_rate'],
                    payload['max_hr'],
                    payload['min_hr'],
                    payload['timestamp'],
                    payload['traceID'])
    session.add(bp)
    session.commit()
    session.close()
    logger.info(f'Stored event heartrateEvent with a trace id of {trace_id}')
    
    logger.info('Connecting to DB. Hostname: {}, Port: {}'.format(app_config['datastore']["hostname"], app_config['datastore']["port"]))
    return "Saved ride reading to db"


def get_heartrate(timestamp):
    """ Gets new heartrate readings after the timestamp """
    logger.info('Connecting to DB. Hostname: {}, Port: {}'.format(app_config['datastore']["hostname"], app_config['datastore']["port"]))
    session = DB_SESSION()
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    readings = session.query(HeartRate).filter(HeartRate.date_created >= timestamp_datetime)
    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())

    session.close()

    logger.info("Query for heartrate data readings after %s returns %d results" % (timestamp, len(results_list)))
    return results_list, 200


def process_messages():
    """ Process event messages """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).

    consumer = topic.get_simple_consumer(consumer_group=b'event_group', 
                                        reset_offset_on_start=False, 
                                        auto_offset_reset=OffsetType.LATEST)

    # This is blocking - it will wait for a new message
    for msg in consumer:
        print(msg)
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]

        if msg["type"] == "ride": # Change this to your event type
        # Store the event1 (i.e., the payload) to the DB
            storeRide(payload)
        elif msg["type"] == "heartrate": # Change this to your event type
            storeHeartrate(payload)
            # Store the event2 (i.e., the payload) to the DB
            # Commit the new message as being read
        consumer.commit_offsets()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)



# def heartrate(body):
#     """ Receives heartrate data event"""

#     logger.info('Connecting to DB. Hostname: {}, Port: {}'.format(app_config['datastore']["hostname"], app_config['datastore']["port"]))
#     session = DB_SESSION()
#     bp = HeartRate(body['user_id'],
#                     body['device_id'],
#                     body['heart_rate'],
#                     body['max_hr'],
#                     body['min_hr'],
#                     body['timestamp'],
#                     body['traceID'])

#     session.add(bp)
#     session.commit()
#     session.close()

#     logger.info('Stored event heartrate request with a trace id of' + body['traceID'])
#     return NoContent, 201

# def ride(body):
#     """ Receives ride data event"""
#     logger.info('Connecting to DB. Hostname: {}, Port: {}'.format(app_config['datastore']["hostname"], app_config['datastore']["port"]))
#     session = DB_SESSION()
#     bp = Ride(body['user_id'], 
#                     body['movie'],
#                     body['timestamp'],
#                     body['avg_speed'],
#                     body['avg_power'],
#                     body['distance'], 
#                     body['traceID'])

#     session.add(bp)

#     session.commit()
#     session.close()

#     logger.info('Stored event ride request with a trace id of' + body['traceID'])
#     return NoContent, 201