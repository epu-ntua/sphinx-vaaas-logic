from kafka import KafkaProducer
from json import dumps
from time import sleep


class Producer:
    def __init__(self, server, port, json_serializer):
        self.server = server
        self.port = port
        self.producer = self.setup(json_serializer)

    def setup(self, _json_serializer):
        try:
            if _json_serializer:
                producer = KafkaProducer(bootstrap_servers=[self.server + ':' + self.port],
                                         value_serializer=lambda x:
                                         dumps(x).encode('utf-8'))
                return producer
            else:
                return None
        except Exception as e:
            print(f'ERROR on setting up kafka producer: {e.__str__()}')

    def send(self, topic, payload):
        try:
            if self.producer is not None:
                self.producer.send(topic=topic, value=payload)
                sleep(5)

        except Exception as e:
            print(f'ERROR on sending data to kafka: {e.__str__()}')
