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
import mysql-connector-python
import pymysql 


MAX_EVENTS = 10
EVENT_FILE = 'events.json'
DB_ENGINE = create_engine('mysql+pymysql://root:delta123@<hostname>:<port>/<db>')
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def ride(body):
    """ Receives ride data event"""

    session = DB_SESSION()



    bp = Ride(body['user_id'], 
                    body['movie'],
                    body['timestamp'],
                    body['avg_speed'],
                    body['avg_power'],
                    body['distance'], 
                    body["traceID"])

    session.add(bp)

    session.commit()
    session.close()

    return NoContent, 201



def heartrate(body):
    """ Receives heartrate data event"""


    session = DB_SESSION()
    
    bp = HeartRate(body['user_id'],
                    body['device_id'],
                    body['heart_rate'],
                    body['max_hr'],
                    body['min_hr'],
                    body['timestamp'],
                    body["traceID"])

    session.add(bp)

    session.commit()
    session.close()


    return NoContent, 201
    


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    app.run(port=8090)