# using pywebostv https://github.com/supersaiyanmode/PyWebOSTV
from flask import Flask, request
from flask_cors import CORS
from pywebostv.discovery import discover, read_location, validate_location
from pywebostv.connection import WebOSClient
from pywebostv.controls import WebOSControlBase, MediaControl, TvControl, SystemControl, ApplicationControl, InputControl, SourceControl
from db.storage import load_store, persist_tv_data, load_tv_channels, load_tv_data, persist_store
from helper import connect_client, load_ip, scan_channels
from channel_checking import obtain_schedule, channel_automation, channel_automation_IR
from collections import OrderedDict
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.combining import AndTrigger
from apscheduler.triggers.interval import IntervalTrigger
from routes.automation import initialiseAutomation
import json

# from flask_apscheduler import APScheduler
# https://viniciuschiele.github.io/flask-apscheduler/index.html
# scheduler = APScheduler()
app = Flask(__name__)
CORS(app)

# Add endpoints from blueprints
from routes.audio import audio as audio_bp
app.register_blueprint(audio_bp)

from routes.channels import channels as channels_bp
app.register_blueprint(channels_bp)

from routes.scan import scan as scan_bp
app.register_blueprint(scan_bp)

from routes.power import power as power_bp
app.register_blueprint(power_bp)

from routes.automation import automation1 as automation1_bp
app.register_blueprint(automation1_bp)

from routes.automation import automation2 as automation2_bp
app.register_blueprint(automation2_bp)

from routes.IR import IR as IR_bp
app.register_blueprint(IR_bp)

if __name__ == "__main__":
    # Run below command if database is corrupted
    # persist_tv_data({})
    initialiseAutomation()
    app.run()



