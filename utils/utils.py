import argparse
import json
import sys
import time
from app_logger.logger import MyLogger


# _log = MyLogger(logger_name=__name__).get_logger()
# _log = app_logger

def get_main_logger(name=__name__):
    return MyLogger(logger_name=name).get_logger()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mode', dest='mode', help='Set the running mode (dev/prod)')
    options = parser.parse_args()

    # Check for errors i.e if the user does not specify the target IP Address
    # Quit the program if the argument is missing
    # While quitting also display an error message
    if not options.mode:
        # Code to handle if interface is not specified
        # parser.error("[-] Please specify the running mode (dev/prod), use --help for more info.")
        get_main_logger().error("[-] Please specify the running mode (dev/prod), use --help for more info.")
    # else:
    #     pass
    return options


def create_result(result_='', items=None, page: int = 1, items_per_page: int = 1, more: str = "", status_code: str = '0'):
    if items is None:
        items = []
    temp = {"page": page,
            "page_size": items_per_page,
            "status_code": status_code,
            "result": result_,
            "more": more,
            "items": items}
    return temp


def getPagination(page_nb, items_per_page):
    offset = 0
    try:
        if (page_nb is not None) and (items_per_page is not None):
            assert isinstance(page_nb, int), '"page_nb" should be of type int'
            assert isinstance(items_per_page, int), '"items_per_page" should be of type int'

            if page_nb > 0:
                offset = (page_nb - 1) * items_per_page
            else:
                offset = items_per_page
            return offset
        else:
            return offset
    except Exception as e:
        # logger.error("Either page_nb or items_per_page is Null " + e.__str__())
        # _log.exception(dmsg('') + "Either page_nb or items_per_page is Null " + e.__str__())
        return offset


def checkpayload(payload, *args):
    if len(payload) > 0:
        return True
    else:
        return False


def checkKeys(payload, *args):
    i = None
    result = False
    if checkpayload(payload):
        for i in args:
            if i in payload:
                result = True
            else:
                result = False
                # logging.error('one of the payload keys was invalid: ' + i)
                # _log.debug(dmsg('') + 'one of the payload keys was invalid: ' + i)
                break
        return result
    else:
        # logging.error('payload was empty')
        # _log.debug(dmsg('') + 'payload was empty')
        return False


def checkValues(payload, *args):
    i = None
    result = False
    # print(payload.get('initiatorID'))
    if checkpayload(payload):
        for i in args:
            if (payload.get(i) is not None) and (payload.get(i) != ''):
                result = True
            else:
                result = False
                # logging.error('payload value is either None or empty: ' + i)
                # _log.debug(dmsg('') + 'payload value is either None or empty: ' + i)
                break
        return result
    else:
        # logging.error('payload was empty')
        # _log.debug(dmsg('') + 'payload was empty')
        return False


def dmsg(text_s):
    import inspect
    import os
    caller_frame = inspect.stack()[1]
    caller_filename = caller_frame.filename
    filename = os.path.splitext(os.path.basename(caller_filename))[0]
    return filename + '.py:' + str(inspect.currentframe().f_back.f_lineno) + '| ' + text_s


def get_pagination_filter(request_arguments):
    arguments = {
        "filter": "first=%s rows=%s sort=%s" % (request_arguments.get('first') if request_arguments.get('first') else 1,
                                                request_arguments.get('rows') if request_arguments.get('rows') else 100,
                                                request_arguments.get('sort') if request_arguments.get('sort') else 'name')
    }
    return arguments


def get_slash():
    if sys.platform == 'win32':
        return '\\'
    else:
        return '/'


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True


def wait_until(smth):
    aa = True
    while aa:
        if smth:
            aa = False
            time.sleep(1)
        else:
            continue


def get_mode():
    options = get_args()
    MODE = 'DEV'
    if options.mode:
        MODE = ('DEV' if options.mode.upper() == 'DEV' else 'PROD')
    else:
        MODE = 'DEV'
    return MODE


def diff_dates(date1, date2):
    diff = date2 - date1

    days, seconds = diff.days, diff.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return days, hours, minutes, seconds


def json_crawler(json_input, lookup_key):
    if isinstance(json_input, dict):
        for k, v in json_input.items():
            if k == lookup_key:
                yield v
            else:
                yield from json_crawler(v, lookup_key)
    elif isinstance(json_input, list):
        for item in json_input:
            yield from json_crawler(item, lookup_key)
