from datetime import datetime 
from apscheduler.schedulers.background import BackgroundScheduler
from .default_test_password import change_password_to_default

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(change_password_to_default, 'interval', days=1)
    scheduler.start()