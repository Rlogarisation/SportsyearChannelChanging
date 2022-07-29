from werkzeug.exceptions import BadRequest
from flask import Blueprint, request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.combining import AndTrigger
from apscheduler.triggers.interval import IntervalTrigger
from channel_checking import obtain_schedule, channel_automation

def initialiseAutomation():
    # Background task scheduler
    # obtain_schedule()
    scheduler = BackgroundScheduler()
    scheduler.start()

    trigger1 = AndTrigger([IntervalTrigger(minutes=0.02)])
    trigger2 = AndTrigger([IntervalTrigger(minutes=0.01)])
    global scheduled_job, scheduled_job2
    scheduled_job = scheduler.add_job(obtain_schedule,trigger1)
    scheduled_job2 = scheduler.add_job(channel_automation,trigger2)

automation = Blueprint('automation', __name__, url_prefix='/automation/')

"""
Pause Automation
Method = POST
"""
@automation.route("/pause", methods=['GET'])
def pause():
    scheduled_job2.pause()
    return {}

"""
Resume Automation
Method = POST
"""
@automation.route("/resume", methods=['GET'])
def resume():
    scheduled_job2.resume()
    return {}
