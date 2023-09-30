import requests
import logging
import json
# from app_logger.logger import MyLogger
from utils.utils import get_main_logger

_log = get_main_logger()


def _check_for_errors(response: requests.models.Response, *args, **kwargs):
    response.raise_for_status(400)
    _log.error(f'| Response contained errors-> Status Code: {response.status_code}')


def _req(response, *args, **kwargs):
    print(response.url)
    _log.info(f'{str(response.method).upper()} request for URL: {response.url}')


def _res(response, *args, **kwargs):
    # print(response.content)
    _log.info(f'| Received response from {response.url} with content-> {response.content}')


def kostis(response, *args, **kwargs):
    print(response)


class HttpClient:
    def __init__(self):
        self.urls = []

    def singleRequest(self, method: str, url: str, body=None, response_handler=None):
        if body is None:
            body = {}
        request = None
        # assert is_json(body) is True, 'Body is NOT JSON serializable!'
        try:
            if method.upper() == 'GET':
                request = (requests.get(url, hooks={'response': [response_handler, _check_for_errors]}) if response_handler else requests.get(url))
            elif method.upper() == 'POST':
                request = (requests.post(url, data=json.dumps(body), hooks={'response': [response_handler, _check_for_errors]}) if response_handler else requests.post(url, data=json.dumps(body)))
            elif method.upper() == 'PUT':
                request = (requests.put(url, data=json.dumps(body), hooks={'response': [response_handler, _check_for_errors]}) if response_handler else requests.put(url, data=json.dumps(body)))
            elif method.upper() == 'DELETE':
                request = (requests.delete(url, hooks={'response': [response_handler, _check_for_errors]}) if response_handler else requests.delete(url))
            _log.info(f'Performed {method} request for URL: {url}')
            return request
        except Exception as e:
            _log.exception(e.__str__())
            return None

    def mapRequests(self, _requests):
        try:
            if _requests:
                q = grequests.map(_requests)
                _log.info(f'Mapped {len(_requests)} requests.')
                return q
            else:
                _log.exception('requests (reqs) was None. Did not perform the request mapping.')
                return None
        except Exception as e:
            _log.exception(e.__str__())
            return None

# c = HttpClient()
# r = c.singleRequest('GET', 'http://127.0.0.1:8000/')
# print(c.mapRequests([r]))
