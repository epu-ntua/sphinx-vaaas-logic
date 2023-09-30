import os

import redis
from utils.utils import get_main_logger, get_mode, is_json
from config.config import get_config
import json

log = get_main_logger('redis_manager')
_conf = get_config()
MODE = get_mode()


def get_redis():
    try:
        with redis.Redis(host=_conf[MODE]['redis_url'], port=_conf[MODE]['redis_port'], db=0) as r:
            return r
    except Exception as e:
        log.error(e.__str__())
        return False


def write_data(_key: str, _value: dict) -> bool:
    try:
        assert isinstance(_value, dict), '_value should be of type Dict'
        get_redis().set(_key, json.dumps(_value))
        return True
    except Exception as e:
        log.error(e.__str__())
        return False


def get_data_by_key(_key: str):
    try:
        if is_json(get_redis().get(_key)):  # if the result is jsonifiable it json loads it
            return json.loads(get_redis().get(_key))
        else:  # else it just returns the result (probably string)
            return get_redis().get(_key)
    except Exception as e:
        log.error(e.__str__())
        return {}


def get_data_by_wildcard(_wildcard: str) -> list:
    try:
        return [{key.decode('utf-8'): get_data_by_key(key) for key in get_redis().keys(_wildcard + '*') if get_redis().keys(_wildcard + '*')}]
    except Exception as e:
        log.error(e.__str__())
        return []


def get_all_data() -> list:
    try:
        return [{key.decode('utf-8'): get_data_by_key(key) for key in get_redis().keys() if get_redis().keys()}]
    except Exception as e:
        log.error(e.__str__())
        return []


def delete_all_keys():
    try:
        r = get_redis()
        for k in r.keys():
            r.delete(r.keys())
    except Exception as e:
        log.error(e.__str__())
        return []


# print(get_all_data())
# print('-----', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))