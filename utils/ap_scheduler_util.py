import datetime
import time
import funasr_service
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from log.logger import log

jobstores = {
    'default': MemoryJobStore()
}

executors = {
    'default': ThreadPoolExecutor(2),
    # 'processpool': ProcessPoolExecutor(3)
}

job_defaults = {
    'coalesce': True,
    'max_instances': 3
}


def job_func():
    print(datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])

def scheduler_start():
    log.info("scheduler_starting...")
    scheduler = BackgroundScheduler(executors=executors, job_defaults=job_defaults)
    scheduler.add_job(funasr_service.task_compensate_send, 'interval', minutes=30)
    scheduler.start()
    log.info("scheduler_start success")
