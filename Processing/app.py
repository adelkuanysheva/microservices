import re
import swagger_ui_bundle
import connexion
from connexion import NoContent
import json
import datetime 
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import mysql.connector
import pymysql 
import yaml
import logging
import logger
import logging.config
import uuid
from base import Base
from stats import Stats
import os
from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger('basicLogger')

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

DB_ENGINE = create_engine("sqlite:///%s" % app_config["datastore"]["filename"])
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def populate_stats():
    """ Periodically update stats """

    logger.info('Start Periodic Processing')

    current_time = datetime.datetime.now()   
    current_time_str = current_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    print("Current time: " + current_time_str)

    if os.path.exists("./stats.sqlite"):
        session = DB_SESSION()
        results = session.query(Stats).order_by(Stats.last_updated.desc()).first()
    else: 
        results = Stats(50000, 20, 10000, 100, datetime.datetime(2022, 10, 13, 1, 2, 3))
    
    logger.info(results.last_updated)
    
    num_r = int(results.num_ride_readings)
    num_h = int(results.num_heartrate_readings)
    last_updated = results.last_updated.strftime("%Y-%m-%dT%H:%M:%SZ")
    logger.info("Last Updated on: " + last_updated)
    print(last_updated)
    
    # Ride GET request
    req_ride = requests.get(app_config['eventstore1']['url'] + '?timestamp=' + last_updated, 
                                    headers={'Content-Type': 'application/json'})

    if req_ride.status_code != 200:
        logger.error("Request has failed!")

    ride_data = req_ride.json()
    print(ride_data)
    ride_len = len(ride_data)
    print(ride_len)
    ride_newlen = ride_len + num_r

    # print the events and find average speed
    ride_max = int(results.max_speed_reading)
    for event in ride_data:
        logger.debug(("Event processed:" + event))
        if int(event["avg_speed"]) > ride_max:
            ride_max = event["avg_speed"]


    ride_oldlenstr = str(ride_len)
    ride_lenstr = str(ride_newlen)
    
    logger.info('Number of ride data events received: ' + ride_oldlenstr)
    logger.debug(ride_data)  

    # Heartrate GET request
    req_heartrate = requests.get(app_config['eventstore2']['url'] + '?timestamp=' + last_updated, 
                                    headers={'Content-Type': 'application/json'})

    if req_heartrate.status_code != 200:
        logger.error("Request has failed!")

    hr_data = req_heartrate.json()
    print(hr_data)
    hr_len = len(hr_data)
    hr_newlen = hr_len + num_h

    hr_max = int(results.max_heartrate_reading)
    for event in ride_data:
        logger.debug(("Event processed: " + event))
        if int(event["avg_speed"]) > hr_max:
            hr_max = event["avg_speed"]

    heartrate_oldlenstr = str(hr_len)
    heartrate_lenstr = str(hr_newlen)
    
    logger.info('Number of heartrate data events received: ' + heartrate_oldlenstr)
    logger.debug(ride_data)  

    stats = Stats(ride_lenstr,
                  ride_max,
                  heartrate_lenstr,
                  hr_max,
                  current_time) 

    logger.debug('''New statistics:\n Number of Ride Readings: %s\n Number of HR Readings %s\n Max Speed Reading %s\n Max HR Reading %s''' 
                    % (stats.num_ride_readings, stats.num_heartrate_readings, 
                    stats.max_speed_reading, stats.max_heartrate_reading))

    session.add(stats)
    session.commit()
    session.close()



def get_stats(timestamp):
    """ Receives statistics data event"""
    
    session = DB_SESSION()
    logger.info('Statistics request started.')
    
    results = session.query(Stats).order_by(Stats.last_updated.desc())
    print(results)
    session.close()
    result_dict = results[0].to_dict()

    if len(result_dict) == 0: 
        return "Statistics do not exist", 404

    logger.debug(f"The last updated statistics are:\n{result_dict}\n")
    logger.info("Statistics request completed.")

    return result_dict, 200


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, use_reloader=False)
