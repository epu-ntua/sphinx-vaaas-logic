from kafka import KafkaConsumer
from json import loads
from time import sleep


class Consumer:
    def __init__(self, server, port, topic, group, json_serializer):
        self.server = server
        self.port = port
        self.topic = topic
        self.group = group
        self.consumer = self.setup(json_serializer)

    def setup(self, _json_serializer):
        try:
            if _json_serializer:
                consumer = KafkaConsumer(
                    self.topic,
                    bootstrap_servers=[self.server + ':' + self.port],
                    auto_offset_reset='earliest',
                    enable_auto_commit=True,
                    group_id=self.group,
                    value_deserializer=lambda x: loads(x.decode('utf-8')))
                return consumer
            else:
                return None
        except Exception as e:
            print(f'ERROR on setting up kafka consumer: {e.__str__()}')

    def get_messages(self):
        try:
            if self.consumer is not None:
                for message in self.consumer:
                    print(message)
            else:
                return None
        except Exception as e:
            print(f'ERROR on getting kafka messages: {e.__str__()}')

    # producer = Producer('10.0.100.200', '9092', json_serializer=True)
    # # for e in range(10):
    # data = {'number': randrange(1, 1000)}
    # #     producer.send('numtest', data)
    # producer.send('numtest', data)
    # sleep(5)
    # consumer = Consumer('10.0.100.200', '9092', 'numtest', 'group-1', True)
    # for message in consumer.consumer:
    #     print(message)
