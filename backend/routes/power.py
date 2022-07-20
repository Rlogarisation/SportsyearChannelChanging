from ipaddress import ip_address
from flask import Blueprint, request
from pywebostv.connection import WebOSClient
from db.storage import load_store
from helper import connect_client, load_ip, load_mac
from pywebostv.controls import SystemControl
from wakeonlan import send_magic_packet

power = Blueprint('power', __name__, url_prefix='/smart/')

def _power_off(uuid):
    # setup client
    client = WebOSClient(load_ip(uuid))
    connect_client(client, uuid)
    system = SystemControl(client)

    system.power_off()
    return {}

def _power_on(uuid):
    send_magic_packet(str(load_mac(uuid)), ip_address=load_ip(uuid))
    print(str(load_mac(uuid)))
    return {}

def _power_toggle(uuid):
    try:
        return _power_off(uuid)
    except:
        return _power_on(uuid)

def _screen_off(uuid):
    # setup client
    client = WebOSClient(load_ip(uuid))
    connect_client(client, uuid)
    system = SystemControl(client)

    system.screen_off()
    return {}

def _screen_on(uuid):
    # setup client
    client = WebOSClient(load_ip(uuid))
    connect_client(client, uuid)
    system = SystemControl(client)

    system.screen_on()
    return {}

# POWER ROUTES BELOW

"""
Turn TV with uuid off
Method = POST
"""
@power.route("/power_off", methods=['POST'])
def power_off():
    data = request.get_json()
    uuid = data['uuid']
    return _power_off(uuid)

"""
Turn TV with uuid on
Method = POST
"""
@power.route("/power_on", methods=['POST'])
def power_on():
    data = request.get_json()
    uuid = data['uuid']
    return _power_on(uuid)

"""
Toggle TV ON/OFF
Method = POST
"""
@power.route("/power_toggle", methods=['POST'])
def power_toggle():
    data = request.get_json()
    uuid = data['uuid']
    return _power_toggle(uuid)

"""
Turn TV screen with uuid OFF
Method = POST
"""
@power.route("/screen_off", methods=['POST'])
def screen_off():
    data = request.get_json()
    uuid = data['uuid']
    return _screen_off(uuid)

"""
Turn TV screen with uuid ON
Method = POST
"""
@power.route("/screen_on", methods=['POST'])
def screen_on():
    data = request.get_json()
    uuid = data['uuid']
    return _screen_on(uuid)
