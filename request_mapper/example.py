import grequests
from app_logger.logger import *
import logging
import time
import json

log = MyLogger(logger_name=__name__).get_logger()
url = 'http://127.0.0.1:8000/'


def is_available(response, *args, **kwargs):
    # print(response.url, 'is available')
    log.info('is available')
    log.info(response.content)


def show_data(response, *args, **kwargs):
    print(response.url, 'content is:', response.content)
    log.info(f'Received response from {response.url} with content-> {response.content}')


post_data = {"ip": "10.0.0.1"}
unsent_request = [grequests.get('http://127.0.0.1:8000/', hooks={'response': [is_available]}),
                  grequests.post('http://127.0.0.1:8000/entities/search/', hooks={'response': [is_available]}, data=json.dumps(post_data))]

print(grequests.map(unsent_request, size=2))
time.sleep(20)

