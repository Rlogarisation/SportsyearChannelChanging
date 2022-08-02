from werkzeug.exceptions import BadRequest
from flask import Blueprint, request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.combining import AndTrigger
from apscheduler.triggers.interval import IntervalTrigger
from channel_checking import obtain_schedule, channel_automation, channel_automation_IR

def initialiseAutomation():
    # Background task scheduler
    obtain_schedule()
    scheduler = BackgroundScheduler()
    scheduler.start()

    trigger1 = AndTrigger([IntervalTrigger(hours=24)])
    trigger2 = AndTrigger([IntervalTrigger(minutes=.1)])
    trigger3 = AndTrigger([IntervalTrigger(minutes=.1)])
    global scheduled_job, scheduled_job2, scheduled_job3
    scheduled_job = scheduler.add_job(obtain_schedule,trigger1)
    scheduled_job2 = scheduler.add_job(channel_automation,trigger2)
    scheduled_job3 = scheduler.add_job(channel_automation_IR,trigger3)
    scheduled_job2.pause()
    scheduled_job3.pause()

automation1 = Blueprint('automation1', __name__, url_prefix='/smart/automation/')
automation2 = Blueprint('automation2', __name__, url_prefix='/ir/automation/')

"""
Pause Smart Automation
Method = POST
"""
@automation1.route("/pause", methods=['POST'])
def pause():
    scheduled_job2.pause()
    return {}

"""
Resume Smart Automation
Method = POST
"""
@automation1.route("/resume", methods=['POST'])
def resume():
    scheduled_job2.resume()
    return {}

"""
Pause Automation IR
Method = POST
"""
@automation2.route("/pause", methods=['POST'])
def pause():
    scheduled_job3.pause()
    return {}

"""
Resume Automation IR
Method = POST
"""
@automation2.route("/resume", methods=['POST'])
def resume_IR():
    scheduled_job3.resume()
    return {}

