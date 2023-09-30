from typing import List

import requests
from request_mapper.http_client import HttpClient
from utils.utils import wait_until, is_json, dmsg, get_args, get_main_logger, create_result, get_mode
import json
from datetime import datetime
import re
from config.config import get_config

_log = get_main_logger()
options = get_args()
MODE = get_mode()
_config = get_config()


class MyVaaasHandler:
    def __init__(self, _conf):
        self.conf = _conf
        self.ports = '4a4717fe-57d2-11e1-9a26-406186ea4fc5'  # All IANA assigned TCP and UDP
        self.scanner = '08b69003-5fc2-4037-a479-93b440211c73'  # OpenVas Default
        self.scan_config = 'daba56c8-73ec-11df-a475-002264764cea'  # Full and Fast
        self.assets_url = self.conf[MODE]['ASSETS_URL'] + ':' + self.conf[MODE]['ASSETS_PORT']
        self.vaaas_url = self.conf[MODE]['VAAAS_URL'] + ':' + self.conf[MODE]['VAAAS_PORT']
        self.http = HttpClient()
        self.entities: list[Entity] = []
        self.targets: list[Target] = []
        self.tasks: list[Task] = []

    def get_entities(self):
        try:
            req = self.http.singleRequest('GET', self.assets_url + '/assets')
            # print(dmsg(''), reqs[0].url)
            if req:
                # results = self.http.mapRequests(req)
                # wait_until(results)  # will wait until results are not None
                # _log.debug(dmsg(''), 'Search Results: ', results)
                if is_json(req.content):
                    # print(json.loads(results[0].content))
                    # self.entities = json.loads(results[0].content, object_hook=lambda d: SimpleNamespace(**d))
                    # print(json.loads(req.content)['message']['items'])
                    self.entities = [Entity(**e) for e in json.loads(req.content)['items']]  # response format is different for Asset Manager. {message:...}
                    # self.entities = json.loads(req.content)  # response format is different for Asset Manager. {message:...}
                    # print(self.entities.message.items[0])
                    # print(self.entities[0])
                else:
                    self.entities = []
                return create_result(result_='GET_ENTITIES_SUCCESS', items=self.entities)
            else:
                raise Exception('Could NOT build requests!')
        except Exception as e:
            _log.exception(dmsg('') + 'GET_ENTITIES_ERROR: ' + e.__str__())
            return create_result(result_='GET_ENTITIES_ERROR', more=e.__str__())

    def get_targets(self):
        try:
            reqs = [self.http.singleRequest('GET', self.vaaas_url + '/targets')]
            if reqs:  # :requests.models.Response
                results = self.http.mapRequests(reqs)
                wait_until(results)  # will wait until results are not None
                # _log.debug(dmsg(''), 'Search Results: ', results)
                # print(type(results[0]))
                if results and is_json(results[0].content):
                    # self.targets = json.loads(results[0].content)['items']
                    # print(json.dumps(self.targets, indent=4))
                    # print(self.targets['target_count']['filtered'])
                    if int(json.loads(results[0].content)['items']['target_count']['filtered']) == 0:
                        self.targets = []
                    elif int(json.loads(results[0].content)['items']['target_count']['filtered']) == 1:
                        # print(json.loads(results[0].content)['items']['target'])
                        self.targets = [json.loads(results[0].content)['items']['target']['@id']]
                    elif int(json.loads(results[0].content)['items']['target_count']['filtered']) > 1:
                        # print(json.loads(results[0].content)['items']['target'])
                        self.targets = [target for target in json.loads(results[0].content)['items']['target']]
                        # print(self.targets)
                    else:
                        raise Exception(dmsg('') + 'GET_TARGETS_ERROR: Something went wrong.')
                    return create_result(result_='GET_TARGETS_SUCCESS', items=self.targets)
                else:
                    raise Exception(dmsg('') + 'GET_TARGETS_ERROR: Request result is NOT JSON serializable. Unexpected content.')
            else:
                raise Exception(dmsg('') + 'GET_TARGETS_ERROR: Could NOT build requests!')
        except Exception as e:
            self.targets = []
            _log.exception(dmsg('') + 'GET_TARGETS_ERROR: ' + e.__str__())
            return create_result(result_='GET_TARGETS_ERROR', more=e.__str__())

    def is_assessed(self, asset):
        return True if asset['assessed'] else False

    def is_active(self, asset):
        # now = datetime.now()
        # modified = datetime.fromtimestamp(asset['modified']['$date'] / 1e3)
        return True if asset['active'] else False

    def create_target(self, entity: dict):
        """
        Creates one target with one IP, named <IP>_<date_time>
        :param entity: Entity()
        :return:{"page": int, "page_size": int, "status_code": int, "result": string, "more": string, "items": list}
        """
        try:
            self.targets = []
            if entity:
                assert isinstance(entity, dict), '"entity" must be a dictionary of Type Entity()'
                new_target = Target()
                new_target.name = entity['ip'] + '_' + str(datetime.now()).replace('-', '_').replace(' ', '_')
                new_target.port_list_id = self.ports
                new_target.hosts = [entity['ip']]
                # print(json.dumps(new_target.__dict__))
                reqs = [self.http.singleRequest('POST', self.vaaas_url + '/targets', new_target.__dict__)]
                if reqs:
                    results = self.http.mapRequests(reqs)
                    wait_until(results)  # will wait until results are not None
                    if results and is_json(results[0].content):
                        # print(results)
                        return create_result(result_='CREATE_TARGET_SUCCESS', items=[True if json.loads(r.content)['items']['@status_text'] == 'ok' else False for r in results if r])
                    else:
                        raise Exception(dmsg('') + 'Did not receive results! Or result content is not JSON serializable')
                else:
                    raise Exception(dmsg('') + 'Could NOT build requests!')
            else:
                return create_result(result_='CREATE_TARGET_ERROR', more='"entities" is empty')
        except AssertionError as ae:
            _log.exception(dmsg('') + 'CREATE_TARGET_ERROR: ' + ae.__str__())
            return create_result(result_='CREATE_TARGET_ERROR', more=ae.__str__())
        except Exception as e:
            _log.exception(dmsg('') + 'CREATE_TARGET_ERROR: ' + e.__str__())
            return create_result(result_='CREATE_TARGET_ERROR', more=e.__str__())

    def delete_targets(self, targets: list):
        """

        :param targets: list of target IDs
        :return: {"page": int, "page_size": int, "status_code": int, "result": string, "more": string, "items": list}
        """
        if targets and (len(targets) > 0):
            try:
                reqs = [self.http.singleRequest('DELETE', self.vaaas_url + '/targets/' + t_id) for t_id in targets]
                if reqs:
                    results = self.http.mapRequests(reqs)
                    wait_until(results)  # will wait until results are not None
                    # print(type(results))  # _log.debug(dmsg(''), 'Search Results: ', results)
                    if results and is_json(results[0].content):
                        # print(results[0].content)
                        return create_result(result_='DELETE_TARGETS_SUCCESS', items=[True if json.loads(r.content)['items']['@status'] == '200' else False for r in results if r],
                                             more=results)
                    else:
                        raise Exception(dmsg('') + 'Request result is NOT JSON serializable. Unexpected content.')
                else:
                    raise Exception(dmsg('') + 'Could NOT build requests!')
            except Exception as e:
                _log.exception(dmsg('') + 'DELETE_TARGETS_ERROR: ' + e.__str__())
                return create_result(result_='DELETE_TARGETS_ERROR', more=e.__str__())
        else:
            return create_result(result_='DELETE_TARGETS_ERROR', more='"self.targets" is empty')

    def create_scan(self, target: dict):
        try:
            assert isinstance(target, dict), dmsg('') + ' "target" should be a dict of type Target'
            if target and len(target) > 0:
                new_scan = Task()
                new_scan.name = target['name'] if 'name' in target else 'no_name_found' + '_' + str(datetime.now()).replace('-', '_').replace(' ', '_')
                new_scan.config_id = self.scan_config
                new_scan.scanner_id = self.scanner
                new_scan.target_id = self.targets[0]
                reqs = [self.http.singleRequest('POST', self.vaaas_url + '/tasks', new_scan.__dict__)]
                if reqs:
                    results = self.http.mapRequests(reqs)
                    wait_until(results)  # will wait until results are not None
                    if results and is_json(results[0].content):
                        # print(dmsg(''), json.loads(results[0].content))
                        return create_result(result_='CREATE_SCAN_SUCCESS', items=[True if json.loads(r.content)['items']['@status'] == '201' else False for r in results])
                    else:
                        raise Exception(dmsg('') + 'Did not receive results! Or result content is not JSON serializable')
                else:
                    raise Exception(dmsg('') + 'Could NOT build requests!')
            else:
                return create_result(result_='CREATE_SCAN_ERROR', more='"self.targets" is either Null or empty')
        except AssertionError as e:
            _log.exception(dmsg('') + 'CREATE_SCAN_ERROR: ' + e.__str__())
            return create_result(result_='CREATE_SCAN_ERROR', more=e.__str__())
        except Exception as e:
            _log.exception(dmsg('') + 'CREATE_SCAN_ERROR: ' + e.__str__())
            return create_result(result_='CREATE_SCAN_ERROR', more=e.__str__())

    def delete_task(self, task):
        try:
            if task and task['@id']:
                reqs = [self.http.singleRequest('DELETE', self.vaaas_url + '/tasks/' + task['@id'])]
                if reqs:
                    results = self.http.mapRequests(reqs)
                    wait_until(results)  # will wait until results are not None
                    if results and is_json(results[0].content):
                        print(dmsg(''), json.loads(results[0].content))
                        return create_result(result_='DELETE_SCAN_SUCCESS', items=[True if json.loads(r.content)['items']['@status'] == '200' else False for r in results])
                    else:
                        raise Exception(dmsg('') + 'Did not receive results! Or result content is not JSON serializable')
                else:
                    raise Exception(dmsg('') + 'Could NOT build requests!')
            else:
                return create_result(result_='DELETE_SCAN_ERROR', more='"scan" is either Null or empty')
        except Exception as e:
            _log.exception(dmsg('') + 'DELETE_SCAN_ERROR: ' + e.__str__())
            return create_result(result_='DELETE_SCAN_ERROR', more=e.__str__())

    def get_tasks(self):  # Task => SCAN
        self.tasks = []
        try:
            reqs = [self.http.singleRequest('GET', self.vaaas_url + '/tasks')]
            if reqs:  # :requests.models.Response
                results = self.http.mapRequests(reqs)
                wait_until(results)  # will wait until results are not None
                # print(json.loads(results[0].content))
                if results and is_json(results[0].content):
                    if int(json.loads(results[0].content)['items']['task_count']['filtered']) == 0:
                        self.tasks = []
                    elif int(json.loads(results[0].content)['items']['task_count']['filtered']) == 1:
                        self.tasks = [json.loads(results[0].content)['items']['task']]
                    else:
                        self.tasks = json.loads(results[0].content)['items']['task']
                    return create_result(result_='GET_TASKS_SUCCESS', items=self.tasks)
                else:
                    raise Exception(dmsg('') + 'Did not receive results! Or result content is not JSON serializable')
            else:
                raise Exception(dmsg('') + 'Could NOT build requests!')
        except Exception as e:
            self.targets = []
            _log.exception(dmsg('') + 'GET_TASKS_ERROR: ' + e.__str__())
            return create_result(result_='GET_TASKS_ERROR', more=e.__str__())

    def start_task(self, task):
        if task:
            # print(self.tasks)
            try:
                reqs = [self.http.singleRequest('GET', self.vaaas_url + '/tasks/' + task['@id'] + '/start')]
                if reqs:  # :requests.models.Response
                    results = self.http.mapRequests(reqs)
                    wait_until(results)  # will wait until results are not None
                    if results and is_json(results[0].content):
                        # print(json.loads(results[0].content))
                        if json.loads(results[0].content)['items']['@status'] == '202':
                            return create_result(result_='START_TASK_SUCCESS')
                        else:
                            raise Exception('Could NOT start task.')
                    else:
                        raise Exception(dmsg('') + 'Did not receive results! Or result content is not JSON serializable')
                else:
                    raise Exception(dmsg('') + 'Could NOT build requests!')
            except Exception as e:
                self.targets = []
                _log.exception(dmsg('') + 'START_TASK_ERROR: ' + e.__str__())
                return create_result(result_='START_TASK_ERROR', more=e.__str__())
        else:
            return create_result(result_='START_TASK_ERROR', more='"self.tasks" is empty')

    # def stop_task(self, task):
    #     print(task)
    #     if task:
    #         # print(self.tasks)
    #         try:
    #             reqs: list[grequests.AsyncRequest] = [self.http.singleRequest('GET', self.vaaas_url + '/tasks/' + task['@id'] + '/stop')]
    #             print(reqs[0].url)
    #             if reqs:  # :requests.models.Response
    #                 results = self.http.mapRequests(reqs)
    #                 wait_until(results)  # will wait until results are not None
    #                 print(results)
    #                 if results and is_json(results[0].content):
    #                     if json.loads(results[0].content)['items']['@status'] == '202':
    #                         return create_result(result_='STOP_TASK_SUCCESS')
    #                     else:
    #                         raise Exception('Could NOT start task.')
    #                 else:
    #                     raise Exception(dmsg('') + 'Did not receive results! Or result content is not JSON serializable')
    #             else:
    #                 raise Exception(dmsg('') + 'Could NOT build requests!')
    #         except Exception as e:
    #             self.targets = []
    #             _log.exception(dmsg('') + 'STOP_TASK_ERROR: ' + e.__str__())
    #             return create_result(result_='STOP_TASK_ERROR', more=e.__str__())
    #     else:
    #         return create_result(result_='STOP_TASK_ERROR', more='"self.tasks" is empty')

    def get_task_progress(self):
        _items = []
        if self.tasks:
            # print(self.tasks)
            try:
                reqs = [self.http.singleRequest('GET', self.vaaas_url + '/tasks/' + self.tasks[0]['@id'])]
                if reqs:  # :requests.models.Response
                    results = self.http.mapRequests(reqs)
                    wait_until(results)  # will wait until results are not None
                    if results and is_json(results[0].content):
                        if int(json.loads(results[0].content)['items']['task_count']['filtered']) == 0:
                            raise Exception('No tasks were found!')
                        elif int(json.loads(results[0].content)['items']['task_count']['filtered']) == 1:
                            # print(json.loads(results[0].content)['items']['task']['progress'])
                            if json.loads(results[0].content)['items']['task']['progress']:
                                return create_result(result_='GET_TASK_PROGRESS_SUCCESS', items=[json.loads(results[0].content)['items']['task']['progress']])
                            else:
                                raise Exception('Task is not running')
                                # _items = json.loads(results[0].content)['items']['task']['status']
                        else:
                            _log.error(dmsg('') + ' Found more than one tasks in repository')
                            if json.loads(results[0].content)['items']['task'][0]['progress']:
                                return create_result(result_='GET_TASK_PROGRESS_SUCCESS', items=[json.loads(results[0].content)['items']['task'][0]['progress']])
                            else:
                                return create_result(result_='GET_TASK_PROGRESS_ERROR', items=[json.loads(results[0].content)['items']['task'][0]['status']],
                                                     more='Task is NOT in "Running" status.')
                    else:
                        raise Exception(dmsg('') + 'Did not receive results! Or result content is not JSON serializable')
                else:
                    raise Exception('Could NOT build request')
            except Exception as e:
                self.targets = []
                _log.exception(dmsg('') + 'GET_TASK_PROGRESS_ERROR: ' + e.__str__())
                return create_result(result_='GET_TASK_PROGRESS_ERROR', more=e.__str__())
        else:
            return create_result(result_='GET_TASK_PROGRESS_ERROR', more='"self.tasks" is empty')

    def is_done(self, task):
        try:
            if task and task['@id']:
                reqs = [self.http.singleRequest('GET', self.vaaas_url + '/tasks/' + task['@id'])]
                if reqs:  # :requests.models.Response
                    results = self.http.mapRequests(reqs)
                    wait_until(results)  # will wait until results are not None
                    if results and is_json(results[0].content):
                        return True if json.loads(results[0].content)['items']['task']['status'] == 'Done' else False  # Requested, Queued, Running
                    else:
                        raise Exception(dmsg('') + 'Did not receive results! Or result content is not JSON serializable')
                else:
                    raise Exception('Could NOT build request')
            else:
                raise Exception(dmsg('') + 'Task does not have an ID!')
        except Exception as e:
            self.targets = []
            _log.exception(dmsg('') + 'IS_DONE_ERROR: ' + e.__str__())
            return create_result(result_='IS_DONE_ERROR', more=e.__str__())

    def get_report(self, task):
        try:
            if task and task['items'][0]['@id']:
                if task['items'][0]['status'] == 'Done':
                    _id = task['items'][0]['last_report']['report']['@id']
                    reqs = [self.http.singleRequest('GET', self.vaaas_url + '/reports/' + _id)]
                    if reqs:  # :requests.models.Response
                        results = self.http.mapRequests(reqs)
                        wait_until(results)  # will wait until results are not None
                        if results and is_json(results[0].content):
                            return create_result(result_='GET_TASK_REPORT_SUCCESS', items=json.loads(results[0].content)['items'])
                        else:
                            raise Exception(dmsg('') + 'Did not receive results! Or result content is not JSON serializable')
                    else:
                        raise Exception('Could NOT build request')
                else:
                    raise Exception(dmsg('') + 'Task is NOT in "Running" status')
            else:
                return create_result(result_='GET_TASK_REPORT_ERROR', more='"task" is empty')
        except Exception as e:
            _log.exception(dmsg('') + 'GET_TASK_REPORT_ERROR: ' + e.__str__())
            return create_result(result_='GET_TASK_REPORT_ERROR', more=e.__str__())

    def update_entities(self):
        pass

    def delete_tasks(self):
        try:
            total = 0
            tasks = self.get_tasks()
            if tasks and tasks['items']:
                for index, t in enumerate(tasks['items']):
                    total = index + 1
                    if t['status'] == 'Running':
                        resultX = self.stop_task(t)
                        _log.debug(resultX)
                        resultY = self.delete_task(t)
                        _log.debug(resultY)
                    else:
                        resultZ = self.delete_task(t)
                        _log.debug(resultZ)
                return create_result(result_='DELETE_TASKS_SUCCESS', more=f'{total} tasks were deleted')
            else:
                raise Exception(dmsg('') + '"entities" was either null or empty')
        except Exception as e:
            _log.exception(dmsg('') + 'DELETE_TASKS_ERROR: ' + e.__str__())
            return create_result(result_='DELETE_TASKS_ERROR', more=e.__str__())


class Entity:
    def __init__(self, _id='', name='', description='', assetType='', modified=False, assessed=False, cvss=0.0, status=False, sensitivity=0, location='', owner='', backupLocation='',
                 dependedServices=None, active=True, hostnames=None, created='', services=None, os=None,
                 assetValue='',
                 ip='', mac='', vendor=''):
        if os is None:
            os = {}
        if services is None:
            services = []
        if hostnames is None:
            hostnames = []
        if dependedServices is None:
            dependedServices = []
        self.os: dict = os
        self.services: List[dict] = services
        self.created = created
        self.modified = modified
        self.id: str = _id
        self.name: str = name
        self.hostnames: List[str] = hostnames
        self.description: str = description
        self.assetType: str = assetType
        self.assessed: bool = assessed
        self.cvss: float = cvss
        self.modified: bool = modified
        self.status: bool = status
        self.sensitivity: int = sensitivity
        self.location: str = location
        self.owner: str = owner
        self.backupLocation: str = backupLocation
        self.dependedServices: str = dependedServices
        self.assetValue: str = assetValue
        self.active: bool = active
        self.ip: str = ip
        self.mac: str = mac
        self.vendor: str = vendor

    def __getitem__(self, key):
        print("Inside `__getitem__` method!")
        return getattr(self, key)


class Target:
    def __init__(self, id='', name='', hosts=None, port_range=None, port_list_id=None):
        if port_list_id is None:
            port_list_id = []
        if port_range is None:
            port_range = []
        if hosts is None:
            hosts = []
        self.id = id
        self.name = name
        self.hosts = hosts
        self.port_range = port_range
        self.port_list_id = port_list_id

    def __getitem__(self, key):
        print("Inside `__getitem__` method!")
        return getattr(self, key)


class Task:
    def __init__(self, id='', name='', config_id='', target_id='', scanner_id=''):
        self.id = id
        self.name = name
        self.config_id = config_id
        self.target_id = target_id
        self.scanner_id = scanner_id

    def __getitem__(self, key):
        print("Inside `__getitem__` method!")
        return getattr(self, key)


def get_task_name(_net: str) -> str:
    return str(re.sub('[^0-9a-zA-Z]+', '_', _net))


def get_latest_report(task):
    return max(task['reports'], key=lambda x: int(x))


def check_task_progress(ip: str):
    try:
        res = requests.post(f'{_config[MODE]["VAAAS_URL"]}:{_config[MODE]["VAAAS_PORT"]}/api/v1/tasks', data=json.dumps({"target": ip}))  # Start scan for specific IP
        status = ''
        progress = 0
        report = {}
        task = {}
        response = json.loads(res.content) if is_json(res.content) else {}
        # print(response)
        if response and ("SUCCESS" in response['result']):
            task = response['items']['task'] if response['items'] and response['items']['task'] else {}
            # print('aaaa', task)
            processes = task['processes'] if task else {}
            if processes.get('SYN Stealth Scan'):
                status = processes.get('SYN Stealth Scan').get('status')
                if status == 'started':
                    # print(task.get('SYN Stealth Scan').get('progress'))
                    progress = float(processes.get('SYN Stealth Scan').get('progress'))
                elif status == 'ended' and task.get('reports'):
                    report = get_latest_report(task)
                return {"status": status, "progress": progress, "report": report}
            else:
                _log.error(dmsg('') + 'SYN Scan has not started yet!')
                return {}
        else:
            _log.error(dmsg('') + f'GET_TASK_RESULT: {response["result"]} - {response["more"]}')
            return {}
    except Exception as e:
        _log.exception(dmsg('') + e.__str__())
        return {}


# while True:
#     print(check_task_progress('10.0.100.98'))
#     time.sleep(2)
if __name__ == '__main__':
    c = get_config()
    v = MyVaaasHandler(c)
    ent = v.get_entities()
    print(ent)
