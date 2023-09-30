import os
import json
import requests
from kafka import KafkaConsumer, KafkaProducer
from kafka.oauth import AbstractTokenProvider
import sys
from utils.utils import get_mode, get_slash
from config.config import get_config
from json import dumps, loads

_config = get_config()

MODE = get_mode()

SM_IP = os.environ.get('SM_IP') if os.environ.get('SM_IP') else _config[MODE]['SM_IP']
KAFKA_USERNAME = os.environ.get('KAFKA_USERNAME') if os.environ.get('KAFKA_USERNAME') else _config[MODE]['KAFKA_USERNAME']
KAFKA_PASSWORD = os.environ.get('KAFKA_PASSWORD') if os.environ.get('KAFKA_PASSWORD') else _config[MODE]['KAFKA_PASSWORD']
OAUTH_CLIENT_ID = os.environ.get('OAUTH_CLIENT_ID') if os.environ.get('OAUTH_CLIENT_ID') else _config[MODE]['OAUTH_CLIENT_ID']
OAUTH_TOKEN_ENDPOINT_URI = os.environ.get('OAUTH_TOKEN_ENDPOINT_URI') if os.environ.get('OAUTH_TOKEN_ENDPOINT_URI') else _config[MODE]['OAUTH_TOKEN_ENDPOINT_URI']
BOOTSTRAP_SERVERS = os.environ.get('BOOTSTRAP_SERVERS') if os.environ.get('BOOTSTRAP_SERVERS') else _config[MODE]['BOOTSTRAP_SERVERS']
KAFKA_CERT = os.environ.get('KAFKA_CERT') if os.environ.get('KAFKA_CERT') else _config[MODE]['KAFKA_CERT']  # FULL PATH OF THE CERTIFICATE LOCATION


class TokenProvider(AbstractTokenProvider):

    def __init__(self, **config):
        super().__init__(**config)
        self.kafka_ticket = json.loads(requests.post(f'{SM_IP}/KafkaAuthentication', data={'username': KAFKA_USERNAME, 'password': KAFKA_PASSWORD}).text)['data']

    def token(self):
        kafka_token = json.loads(requests.get(OAUTH_TOKEN_ENDPOINT_URI, auth=(OAUTH_CLIENT_ID, self.kafka_ticket)).text)['access_token']

        return kafka_token


# KAFKA CLIENT PRODUCER
class MykafkaProducer:
    def __init__(self):
        # self.producer = None
        self.app_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        try:
            self.producer = KafkaProducer(bootstrap_servers=BOOTSTRAP_SERVERS,
                                          security_protocol='SASL_SSL',
                                          sasl_mechanism='OAUTHBEARER',
                                          sasl_oauth_token_provider=TokenProvider(),
                                          ssl_cafile=os.path.join(os.path.join(self.app_path, 'env_values'), KAFKA_CERT),
                                          value_serializer=lambda x: dumps(x).encode('utf-8'))
        except Exception as e:
            print(f'ERROR initializing Kafka Producer: {e.__str__()}')

    def get_producer(self):
        return self.producer

    def send_topic(self, _producer: KafkaProducer = None, _topic='vaaas_report', _data=None):
        prod = _producer if _producer else self.producer
        dat = _data if _data else {'data': {'some_key': 'some_value'}}
        try:
            prod.send(_topic, dat)
            prod.flush()
        except Exception as e:
            print(f'ERROR on sending message to kafka topic: {e.__str__()}')


# KAFKA CLIENT CONSUMER
class MyKafkaConsumer:
    def __init__(self):
        # self.consumer = None
        self.app_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        try:
            self.consumer = KafkaConsumer(bootstrap_servers=BOOTSTRAP_SERVERS,
                                          auto_offset_reset='earliest',
                                          security_protocol='SASL_SSL',
                                          sasl_mechanism='OAUTHBEARER',
                                          sasl_oauth_token_provider=TokenProvider(),
                                          ssl_cafile=os.path.join(os.path.join(self.app_path, 'env_values'), KAFKA_CERT),
                                          value_deserializer=lambda y: loads(y.decode('utf-8')))
        except Exception as e:
            print(f'ERROR initializing Kafka Consumer: {e.__str__()}')

    def get_consumer(self):
        return self.consumer

    def subscribe_to_topic(self, _consumer: KafkaConsumer = None, _topic='python-topic'):
        cons = _consumer if _consumer else self.consumer
        try:
            cons.subscribe([_topic])
        except Exception as e:
            print(f'ERROR subscribing to topic: {e.__str__()}')

    def print_topic_messages(self, _consumer: KafkaConsumer = None, ):
        cons = _consumer if _consumer else self.consumer
        try:
            if cons is not None:
                for msg in cons:
                    print(f'Topic: {msg.topic}, partition: {msg.partition}, offset: {msg.offset}, key: {msg.key}, value: {msg.value}')
            else:
                print('Consumer was None')
        except Exception as e:
            print(f'ERROR on getting kafka messages: {e.__str__()}')
