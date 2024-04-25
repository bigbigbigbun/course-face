from apscheduler.schedulers.background import BackgroundScheduler
# from ..models.models import *


scheduler = BackgroundScheduler()


def job1():
    print('111')


scheduler.add_job(job1, 'cron', hour=9, minute=42)
# scheduler.add_job(job2, 'cron', hour=14, minute=30)
# scheduler.add_job(job3, 'interval', seconds=30, max_instances=5)
# scheduler.start()