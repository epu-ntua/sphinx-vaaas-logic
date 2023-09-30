from threading import Thread
from apscheduler.schedulers.background import BackgroundScheduler
from sanic import Sanic
from sanic.response import json as sanic_json
from config.config import get_config
from utils.utils import get_main_logger, get_mode, dmsg
from vaaas_handler.logic import start_assessments, get_latest_reports

tools = {}


def setup_module(mode):
    tools['app'] = Sanic(__name__)
    tools['log'] = get_main_logger('main.py')
    _c = tools['conf'] = get_config()
    # tools['sched'] = Scheduler()
    tools['sched']: BackgroundScheduler = BackgroundScheduler(daemon=True)

    tools['sched'].add_job(replace_existing=True, func=start_assessments, trigger='cron', day_of_week='mon-fri', hour=2, minute=0, timezone='Europe/Athens')

    tools['sched'].add_job(replace_existing=True, func=get_latest_reports, trigger='cron', day_of_week='mon-fri', hour=4, minute=0, timezone='Europe/Athens')

    tools['sched'].start()


setup_module(mode=get_mode())
app = tools['app']


@app.get("/")
async def home(request):
    tools.get('log').debug(dmsg('') + ' This is the Logic home endpoint.')
    return sanic_json({"message": ' This is the Logic home endpoint.'}, status=200)


@app.get('/health')
async def health(request):
    return sanic_json({'result': 'This is the vulnerability assessment LOGIC component'}, status=200)


@app.get('/scans')
async def scans(resuest):
    Thread(target=start_assessments, args=[]).start()
    return sanic_json({"message": "Starting Scanning all un-assessed entities."}, status=200)


@app.get('/reports')
async def reports(resuest):
    Thread(target=get_latest_reports, args=[]).start()
    return sanic_json({"message": "Starting sending all assessment reports."}, status=200)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8005)
