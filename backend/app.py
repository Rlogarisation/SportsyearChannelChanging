# using pywebostv https://github.com/supersaiyanmode/PyWebOSTV
from flask import Flask, request
from scan import LGTVScan
from pywebostv.discovery import discover, read_location, validate_location
from pywebostv.connection import WebOSClient
from pywebostv.controls import WebOSControlBase, MediaControl, TvControl, SystemControl, ApplicationControl, InputControl, SourceControl
from db.storage import load_store
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

@app.route("/scan")
def ScanTV():
    results = LGTVScan()
    if len(results) > 0:
        print (json.dumps({
            "result": "ok",
            "count": len(results),
            "list": results
        }, sort_keys=True, indent=4))
    else:
        print (json.dumps({
            "result": "failed",
            "count": len(results)
        }, sort_keys=True, indent=4))
    return {
        "scan" : results
    }

if __name__ == "__main__":
    # Setup IPs
    # tv_ips = ScanTV()
    # persist_tv_ips(tv_ips)

    tv_id = 0

    # Setup initial registration/connection to client
    client = WebOSClient(load_ip(tv_id))
    connect_client(client, load_store())

    # Store channel data in db
    scan_channels(tv_id)

    app.run()