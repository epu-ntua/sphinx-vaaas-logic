from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from pytz import utc
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.schedulers.blocking import BlockingScheduler
# from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from utils.utils import dmsg, get_main_logger

_log = get_main_logger()


class Scheduler:
    def __init__(self):
        self.executors = {
            'default': ThreadPoolExecutor(20),
            'processpool': ProcessPoolExecutor(5)
        }
        self.job_defaults = {
            'coalesce': False,
            'max_instances': 1,
            'replace_existing': True,
            # 'misfire_grace_time': 2 * 30,
        }
        self.jobstores = {
            #     'mongo': MongoDBJobStore(),
            'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
        }
        try:
            # jobstores = self.jobstores,
            self.sched = BackgroundScheduler(executors=self.executors, jobstores=self.jobstores, job_defaults=self.job_defaults, timezone="Europe/Athens")
            # self.sched = BlockingScheduler(executors=self.executors, job_defaults=self.job_defaults, timezone=utc)
            self.sched.add_listener(self.scheduler_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        except Exception as e:
            _log.exception(dmsg('') + 'Error during scheduler init :(  --> ' + e.__str__())

    def scheduler_listener(self, event):
        if event.exception:
            print('The job crashed :(')
            _log.debug(dmsg('') + 'The job crashed :(')
        else:
            _log.debug(dmsg('') + 'The job has finished :-)')

    def add_cron_job(self, function, kwargs):
        """
        :param function: function tp be executed
        :param kwargs: {'year': 4-digit year,
                        'month':month(1-12),
                        'day':day(1-31),
                        'day_of_the_week':(int|str) – number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun),
                        'hour':(int|str) – hour (0-23),
                        'minute':(int|str) – minute (0-59),
                        'start_date':(datetime|str) – earliest possible date/time to trigger on (inclusive),
                        'end_date':(datetime|str) – latest possible date/time to trigger on (inclusive),
                        'timezone': (datetime.tzinfo|str) – time zone to use for the date/time calculations (defaults to scheduler timezone),
                        'jitter':(int|None) – advance or delay the job execution by jitter seconds at most
        :return: a job instance
        """
        try:
            # max_instances = 1, coalesce = True, misfire_grace_time = 2 ** 30,
            job = self.sched.add_job(replace_existing=True, func=function, trigger='cron', **kwargs)
            return job
        except Exception as e:
            _log.exception(dmsg('') + 'Could not add job to scheduler :(  --> ' + e.__str__())
            return None

    def start_sched_jobs(self):
        return self.sched.start()

    def get_sched_jobs(self):
        return self.sched.get_jobs()

    def get_state(self):
        return self.sched.state
