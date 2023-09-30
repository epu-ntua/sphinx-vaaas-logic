import json
import re
import time
from datetime import datetime
import os
from threading import Thread

import requests

from MyKafkaClient.My_Kafka_Client import MykafkaProducer, MyKafkaConsumer
from config.config import get_config
from report_parser.nmap_report_parser import ReportParser
from utils.utils import diff_dates, get_mode
from utils.utils import get_main_logger, dmsg
from utils.utils import is_json
from vaaas_handler.handler import MyVaaasHandler, Entity

_log = get_main_logger()
MODE = get_mode()
_conf = get_config()
vaaas_url = os.environ.get('VAAAS_URL') if os.environ.get('VAAAS_URL') else _conf[MODE]['VAAAS_URL']
vaaas_port = os.environ.get('VAAAS_PORT') if os.environ.get('VAAAS_PORT') else _conf[MODE]['VAAAS_PORT']
assets_url = os.environ.get('ASSETS_URL') if os.environ.get('ASSETS_URL') else _conf[MODE]['ASSETS_URL']
assets_port = os.environ.get('ASSETS_PORT') if os.environ.get('ASSETS_PORT') else _conf[MODE]['ASSETS_PORT']
AT = _conf[MODE]['ASSESSMENT_THRESHOLD']


def get_task_name(_net: str) -> str:
    return str(re.sub('[^0-9a-zA-Z]+', '_', _net))


def get_which_assets_should_be_assessed(_entities: [Entity]) -> [Entity]:
    _for_reassessment: [Entity] = []
    #  Select which entities should be (re) assessed
    for e in _entities:  # FOR EACH ENTITY
        # print(e.ip)
        if e.assessed:  # IS IT ASSESSED -> if the entity is assessed before, we will check when. if 5 or more days have passed, it will be reassessed ?
            now = datetime.now()
            mts = datetime.fromtimestamp(e.modified['$date'] / 1000.0)
            d, h, m, s = diff_dates(mts, now)
            if d > AT:  # if the days (d) past from the previous modification exceed 5 (AT), then re-assess # IF YES...HAVE X DAYS PAST SINCE?
                _for_reassessment.append(e)  # ADD TO LIST FOR ASSESSMENT
            else:
                pass  # else do nothing
        else:  # if the entity has not been assessed it will be added for assessment
            _for_reassessment.append(e)  # ADD TO LIST FOR ASSESSMENT
    return _for_reassessment


def update_asset_assessed_status(asset_id: str, asset_status: bool) -> bool:
    try:
        upd = requests.put(f'{assets_url}:{assets_port}/entities/{asset_id}', data=json.dumps({"assessed": asset_status}))  # update entity as assessed
        if is_json(upd.content):
            print(json.loads(upd.content))
            _log.debug(json.loads(upd.content))  # TODO CHECK IF RESULT IS SUCCESSFUL
            return True
        else:
            _log.error(dmsg('') + f' Unexpected response from assets API for ID: {asset_id}. Could not update Entity')
            return False
    except Exception as e:
        _log.exception(e.__str__())
        return False


def start_asset_assessment(assessment_name: str, asset_ip: str, assessment_speed: int = 3) -> bool:
    try:
        res = requests.post(f'{vaaas_url}:{vaaas_port}/tasks/start', data=json.dumps({"name": assessment_name, "target": asset_ip, "speed": assessment_speed}))  # Start scan for specific IP

        if is_json(res.content):
            _log.debug(res.content)
            if json.loads(res.content).get('result') == 'SCAN_NETWORK_STARTED':  # if request is successful
                return True
            else:
                _log.error(f'Scan for {asset_ip} did NOT start!!')
                return False
        else:
            _log.error(f'Got unexpected result for "start_scan" for ip: {asset_ip}')
            return False
    except Exception as e:
        _log.exception(e.__str__())
        return False


def start_assessments():
    _log.debug('Starting assessments...')
    try:
        h = MyVaaasHandler(_conf)
        entities: [Entity] = h.get_entities().get('items')  # 1: GET ENTITIES

        # assets_for_reassessment: [Entity] = get_which_assets_should_be_assessed(entities)
        #
        # not_started = assets_for_reassessment.copy()  # duplicate the array for manipulation
        #
        for i in entities:  # for each entity eligible for assessment (i is of type Entity)
            _log.debug(dmsg('') + f'starting assessment for {i.ip}')
            #
            Thread(target=start_asset_assessment, kwargs={'assessment_name': i.ip, 'asset_ip': i.ip, 'assessment_speed': 3}).start()
            time.sleep(5)  # sleep for 1 second - give the API time to breath
            # i.assessed is a boolean. True if the assessment has started. False if it didnt
        #     not_started.pop(not_started.index(i)) if update_asset_assessed_status(i.id.get("$oid"), i.assessed) else None  # pop the entity from the not_started array
        # (assessment_name=i.ip, asset_ip=i.ip, assessment_speed=3)
        # _log.debug(f'{len(not_started)} assessments did not start! IPs: [{[i.ip for i in not_started if len(not_started)]}]')
    except Exception as e:
        _log.exception(e.__str__())


def setup_kafka():
    p = MykafkaProducer()
    # p.send_topic(_producer=p.get_producer(), _topic='vaaas_reports', _data={'data': {'vaaas_reports': 'Test'}})
    c = MyKafkaConsumer()
    # c.subscribe_to_topic(_consumer=c.get_consumer(), _topic='vaaas_reports')
    # c.print_topic_messages()
    return p, c


def get_tasks_from_vaaas() -> dict:
    try:
        _tasks = None
        res = requests.get(f'{vaaas_url}:{vaaas_port}/tasks')  # GET tasks from vaaas
        # print(res.content)
        _result = json.loads(res.content) if is_json(res.content) else {}
        _tasks = _result.get('items', []).get('tasks', {})
        _log.debug(f"Got {len(_tasks)} tasks")
        return _tasks
    except Exception as e:
        _log.exception(e.__str__())
        return {}


def get_latest_reports():
    try:
        tasks: dict = get_tasks_from_vaaas()
        _log.debug(tasks)
        latest_reports = []
        if tasks:
            # _log.debug('INTO TASKS')
            for t in tasks:
                for key, value in t.items():
                    # print(key)
                    reports = value.get('reports') if value.get('reports') else {}
                    latest_key = max(reports.keys(), key=lambda x: int(x)) if reports else ''
                    # print(latest_key)
                    # rep = ReportParser(value.get('reports').get(latest_key)).get_stix_report() if latest_key else {}
                    latest_reports.append({key: value.get('reports').get(latest_key)}) if value.get('reports') else None
        _p, _c = setup_kafka()
        if _p.get_producer() and _c.get_consumer():
            for _r in latest_reports:
                _log.debug(_r)
                if _r:
                    _log.debug('Sending VAaaS report To Kafka')
                    _p.send_topic(_producer=_p.get_producer(), _topic='vaaas-reports', _data={'data': {'vaaas-reports': json.dumps(_r)}})

            # _c.subscribe_to_topic(_consumer=_c.get_consumer(), _topic='vaaas-reports')
            # _c.print_topic_messages()
        else:
            _log.error('Either Kafka consumer, or Kafka producer is None')
    except Exception as e:
        _log.exception(e.__str__())

#
#
# get_latest_reports()
