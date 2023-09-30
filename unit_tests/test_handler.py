import unittest
from config.config import get_config
from vaaas_handler.handler import MyVaaasHandler
from utils.utils import is_json
import json

# from utils.utils import wait_until, is_json, dmsg, get_args

_conf = get_config()
#
h = MyVaaasHandler(_conf)


class TestLogicHandler(unittest.TestCase):
    # @unittest.skip
    def test_0000_get_entities(self):
        result1 = h.get_entities()
        # print(result1)
        self.assertEqual('GET_ENTITIES_SUCCESS', result1['result'])

    # @unittest.skip
    def test_0001_get_targets(self):
        result1 = h.get_targets()
        # print(result1)
        self.assertEqual('GET_TARGETS_SUCCESS', result1['result'])

    # @unittest.skip
    def test_0010_is_assessed(self):
        result1 = h.get_entities()
        if result1['result']:
            self.assertEqual('GET_ENTITIES_SUCCESS', result1['result'])
            result2 = h.is_assessed(result1['items'][0] if result1['items'] else [])
            self.assertIn(result2, [True, False])

    # @unittest.skip
    def test_0011_is_active(self):
        result1 = h.get_entities()
        print(result1)
        if result1['result']:
            self.assertEqual('GET_ENTITIES_SUCCESS', result1['result'])
            result2 = h.is_active(result1['items'][0])
            self.assertIn(result2, [True, False])

    # @unittest.skip
    def test_0100_create_target(self):
        result1 = h.get_entities()
        self.assertEqual('GET_ENTITIES_SUCCESS', result1['result'])
        result2 = h.create_target(result1['items'])
        self.assertEqual('CREATE_TARGET_SUCCESS', result2['result'])
        result3 = h.create_target(result1['items'][0]) if result1['items'] else result1['items']
        # print(result3)
        self.assertEqual('CREATE_TARGET_ERROR', result3['result'])

    # @unittest.skip
    def test_0101_delete_targets(self):
        result1 = h.delete_targets()
        # print(result1)
        self.assertEqual('DELETE_TARGETS_SUCCESS', result1['result'])

    # @unittest.skip
    def test_0110_get_scan(self):
        result1 = h.get_tasks()
        # print(result1)
        self.assertEqual('GET_TASKS_SUCCESS', result1['result'])

    # @unittest.skip
    def test_0111_create_scan(self):
        result1 = h.get_entities()
        self.assertEqual('GET_ENTITIES_SUCCESS', result1['result'])
        result2 = h.create_target(result1['items'])
        self.assertEqual('CREATE_TARGET_SUCCESS', result2['result'])
        result3 = h.get_targets()
        self.assertEqual('GET_TARGETS_SUCCESS', result3['result'])
        targets = result3['items']
        result4 = h.create_scan(targets)
        # print(result4)
        self.assertEqual('CREATE_SCAN_SUCCESS', result4['result'])
        result5 = h.get_tasks()
        # # print(result5)
        # self.assertEqual('GET_TASKS_SUCCESS', result5['result'])
        # result6 = h.delete_scan(result5['items'][0])
        # self.assertEqual('DELETE_SCAN_SUCCESS', result6['result'])
        # result7 = h.delete_targets()
        # # print(result1)
        # self.assertEqual('DELETE_TARGETS_SUCCESS', result7['result'])

    # @unittest.skip
    def test_1000_start_scan(self):
        result1 = h.get_entities()
        self.assertEqual('GET_ENTITIES_SUCCESS', result1['result'])
        result2 = h.create_target(result1['items'])
        self.assertEqual('CREATE_TARGET_SUCCESS', result2['result'])
        result3 = h.get_targets()
        self.assertEqual('GET_TARGETS_SUCCESS', result3['result'])
        targets = result3['items']
        result4 = h.create_scan(targets)
        # print(result4)
        self.assertEqual('CREATE_SCAN_SUCCESS', result4['result'])
        result5 = h.get_tasks()
        self.assertEqual('GET_TASKS_SUCCESS', result5['result'])
        # print(result5)
        result6 = h.start_task(result5['items'][0])
        self.assertEqual('START_TASK_SUCCESS', result6['result'])
        # result7 = h.stop_task(result5['items'][0])
        # self.assertEqual('STOP_TASK_SUCCESS', result7['result'])

    def test_1001_cleanup(self):  # todo NOT WORKING
        result1 = h.get_tasks()
        self.assertEqual('GET_TASKS_SUCCESS', result1['result'])
        # print(result1)
        if result1 and result1['items']:
            for r in result1['items']:
                # print(r)
                if r['status'] == 'Running':
                    # print(r)
                    resultX = h.stop_task(r)
                    self.assertEqual('STOP_TASK_SUCCESS', resultX['result'])
                    resultY = h.delete_task(r)
                    self.assertEqual('DELETE_SCAN_SUCCESS', resultY['result'])
                else:
                    resultY = h.delete_task(r)
                    self.assertEqual('DELETE_SCAN_SUCCESS', resultY['result'])
        result2 = h.delete_targets()
        # print(result2)
        self.assertEqual('DELETE_TARGETS_SUCCESS', result2['result'])
