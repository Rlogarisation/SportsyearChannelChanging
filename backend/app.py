# using pywebostv https://github.com/supersaiyanmode/PyWebOSTV
from flask import Flask, request
from flask_cors import CORS
from pywebostv.discovery import discover, read_location, validate_location
from pywebostv.connection import WebOSClient
from pywebostv.controls import WebOSControlBase, MediaControl, TvControl, SystemControl, ApplicationControl, InputControl, SourceControl
from db.storage import load_store, persist_tv_data, load_tv_channels, load_tv_data, persist_store
from helper import connect_client, load_ip, scan_channels
from channel_checking import obtain_schedule, channel_automation
from collections import OrderedDict
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.combining import AndTrigger
from apscheduler.triggers.interval import IntervalTrigger
import json


# from flask_apscheduler import APScheduler
# https://viniciuschiele.github.io/flask-apscheduler/index.html
# scheduler = APScheduler()
app = Flask(__name__)
CORS(app)
# Background task scheduler
# scheduler.init_app(app)
# scheduler.start()
init_flag = 0
obtain_schedule()
scheduler = BackgroundScheduler()
scheduler.start()
trigger1 = AndTrigger([IntervalTrigger(minutes=0.5)])
trigger2 = AndTrigger([IntervalTrigger(minutes=0.1)])
scheduled_job = scheduler.add_job(obtain_schedule,trigger1)
scheduled_job2 = scheduler.add_job(channel_automation,trigger2)

# Add endpoints from blueprints
from routes.audio import audio as audio_bp
app.register_blueprint(audio_bp)

from routes.channels import channels as channels_bp
app.register_blueprint(channels_bp)

from routes.scan import scan as scan_bp
app.register_blueprint(scan_bp)

from routes.power import power as power_bp
app.register_blueprint(power_bp)

if __name__ == "__main__":
    # Run below command if database is corrupted
    # persist_tv_data({})
    app.run()

