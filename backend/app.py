# using pywebostv https://github.com/supersaiyanmode/PyWebOSTV
from flask import Flask, request
from scan import LGTVScan
from pywebostv.discovery import discover, read_location, validate_location
from pywebostv.connection import WebOSClient
from pywebostv.controls import WebOSControlBase, MediaControl, TvControl, SystemControl, ApplicationControl, InputControl, SourceControl
from db.storage import load_store
from helper import connect_client, load_ip
import json
# from flask_apscheduler import APScheduler
# https://viniciuschiele.github.io/flask-apscheduler/index.html
# scheduler = APScheduler()
app = Flask(__name__)
# Background task scheduler
# scheduler.init_app(app)
# scheduler.start()

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
    # tv_ips = ScanTV()
    # persist_tv_ips(tv_ips)

    # Setup initial registration/connection to client
    client = WebOSClient(load_ip(0))
    connect_client(client, load_store())

    app.run()