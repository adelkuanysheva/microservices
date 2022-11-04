import connexion
from connexion import NoContent
import requests
import json
from pykafka import KafkaClient
import yaml
import json
import datetime
from flask_cors import CORS, cross_origin
"""
Start event
bin/zookeeper-server-start.sh ./config/zookeeper.properties
bin/kafka-server-start.sh ./config/server.properties

Create Event
bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic events

Delete Event
/bin/kafka-topics.sh --zookeeper localhost:2181 --delete --topic events
"""

with open("app_conf.yaml", 'r') as f:
    app_conf = yaml.safe_load(f.read())

    client = KafkaClient(
        hosts=app_conf['kafka']['server'] + ':' + app_conf['kafka']['port'])
    topic = client.topics[app_conf['kafka']['topic']]
    producer = topic.get_sync_producer()

# functions
def orders_post(orderFormRequest):
    """Logs the order form event into Kafka"""
    print(orderFormRequest)
    msg = {
        "type": "order_form",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": orderFormRequest
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode("utf-8"))

    return NoContent


def repair_request(repairRequestForm):
    """Logs the repair form event into Kafka"""
    print(repairRequestForm)
    msg = {
        "type": "repair_form",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": repairRequestForm
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode("utf-8"))

    return NoContent


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml")

if __name__ == "__main__":
    app.run(port=8080)



