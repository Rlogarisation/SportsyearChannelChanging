from ipaddress import ip_address
from flask import Blueprint, request
from pywebostv.connection import WebOSClient
from db.storage import load_store
from helper import connect_client, load_ip, load_mac
from pywebostv.controls import SystemControl
from wakeonlan import send_magic_packet

power = Blueprint('power', __name__, url_prefix='/smart/<uuid>/')

"""
Turn tv with uuid off
Method = POST
"""
@power.route("/power_off", methods=['POST'])
def power_off(uuid):
    # setup client
    client = WebOSClient(load_ip(uuid))
    connect_client(client, uuid)
    system = SystemControl(client)

    system.power_off()
    return {}

"""
Turn tv with uuid on
Method = POST
"""
@power.route("/power_on", methods=['POST'])
def power_on(uuid):
    send_magic_packet(str(load_mac(uuid)), ip_address=load_ip(uuid))
    # send_magic_packet("b4:b2:91:41:7e:32")
    print(str(load_mac(uuid)))
    return {}

"""
Turn tv screen with uuid OFF
Method = POST
"""
@power.route("/screen_off", methods=['POST'])
def screen_off(uuid):
    # setup client
    client = WebOSClient(load_ip(uuid))
    connect_client(client, uuid)
    system = SystemControl(client)

    system.screen_off()
    return {}
    
"""
Turn tv screen with uuid ON
Method = POST
"""
@power.route("/screen_on", methods=['POST'])
def screen_on(uuid):
    # setup client
    client = WebOSClient(load_ip(uuid))
    connect_client(client, uuid)
    system = SystemControl(client)

    system.screen_on()
    return {}
