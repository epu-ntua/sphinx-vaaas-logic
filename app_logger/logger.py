import logging
import sys, os
import datetime
from logging.handlers import RotatingFileHandler


# Logger.exception() dumps a stack trace along with it. Call this method only from an exception handler.
class MyLogger:
    def __init__(self, logger_name=__name__, level=logging.DEBUG, file_size=2, backup=0):
        self.script_path = os.path.abspath(__file__)
        self.script_dir = os.path.split(self.script_path)[0]
        self.logger_name = logger_name
        self.level = level
        self.logger = logging.getLogger(self.logger_name)
        self.logger.setLevel(self.level)
        self.formatter = logging.Formatter('%(name)s %(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s')
        self.fh = RotatingFileHandler(os.path.join(self.script_dir, '{:%Y-%m-%d}'.format(datetime.datetime.now()) + '.log'), maxBytes=file_size * 1000, backupCount=backup)
        # self.fh = logging.FileHandler(sys.path[1] + '\\' + '{:%Y-%m-%d}'.format(datetime.datetime.now()) + '.log')
        self.fh.setLevel(self.level)
        self.sh = logging.StreamHandler()
        self.sh.setLevel(self.level)
        self.fh.setFormatter(self.formatter)
        self.sh.setFormatter(self.formatter)
        self.logger.addHandler(self.fh)
        self.logger.addHandler(self.sh)

    def set_level(self, level):
        self.logger.setLevel(level)
        self.fh.setLevel(level)
        self.sh.setLevel(level)

    def get_logger(self):
        return self.logger


