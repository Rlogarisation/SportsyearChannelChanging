# using pywebostv https://github.com/supersaiyanmode/PyWebOSTV
from flask import Flask, request
from routes.scan import LGTVScan
from pywebostv.discovery import discover, read_location, validate_location
from pywebostv.connection import WebOSClient
from pywebostv.controls import WebOSControlBase, MediaControl, TvControl, SystemControl, ApplicationControl, InputControl, SourceControl
from db.storage import load_store, persist_tv_ips
from helper import connect_client, load_ip, scan_channels
import json
# from flask_apscheduler import APScheduler
# https://viniciuschiele.github.io/flask-apscheduler/index.html
# scheduler = APScheduler()
app = Flask(__name__)
# Background task scheduler
# scheduler.init_app(app)
# scheduler.start()

# Add endpoints from blueprints
from routes.audio import audio as audio_bp
app.register_blueprint(audio_bp)

from routes.channels import channels as channels_bp
app.register_blueprint(channels_bp)

from routes.scan import scan as scan_bp
app.register_blueprint(scan_bp)

from routes.power import power as power_bp
app.register_blueprint(power_bp)

@app.route("/smart/<tv_id>/raise_volume", methods=['POST'])
def raise_volume(tv_id):
    client = WebOSClient(load_ip(int(tv_id)))
    connect_client(client, load_store())
    media = MediaControl(client)
    media.volume_up()
    return {}

@app.route("/smart/<tv_id>/lower_volume", methods=['POST'])
def lower_volume(tv_id):
    client = WebOSClient(load_ip(int(tv_id)))
    connect_client(client, load_store())
    media = MediaControl(client)
    media.volume_down()
    return {}

if __name__ == "__main__":
    # Setup IPs
    tv_ips = LGTVScan()
    persist_tv_ips(tv_ips)

    tv_id = 0

    # Setup initial registration/connection to client
    client = WebOSClient(load_ip(0))
    connect_client(client, load_store())

    # Store channel data in db
    scan_channels(tv_id)

    app.run()