from ipaddress import ip_address
from flask import Blueprint, request
from pywebostv.connection import WebOSClient
from db.storage import load_store
from helper import connect_client, load_ip, load_mac
from pywebostv.controls import SystemControl
from wakeonlan import send_magic_packet

power = Blueprint('power', __name__, url_prefix='/smart')

"""
Turn tv with tv_id off
Method = POST
"""
@power.route("/<tv_id>/power_off", methods=['POST'])
def power_off(tv_id):
    # setup client
    client = WebOSClient(load_ip(int(tv_id)))
    connect_client(client, load_store())
    system = SystemControl(client)

    system.power_off()
    return {}

"""
Turn tv with tv_id on
Method = POST
"""
@power.route("/<tv_id>/power_on", methods=['POST'])
def power_on(tv_id):
    send_magic_packet(str(load_mac(int(tv_id))), ip_address=load_ip(int(tv_id)))
    # send_magic_packet("b4:b2:91:41:7e:32")
    print(str(load_mac(int(tv_id))))
    return {}

"""
Turn tv screen with tv_id OFF
Method = POST
"""
@power.route("/<tv_id>/screen_off", methods=['POST'])
def screen_off(tv_id):
    # setup client
    client = WebOSClient(load_ip(int(tv_id)))
    connect_client(client, load_store())
    system = SystemControl(client)

    system.screen_off()
    return {}
    
"""
Turn tv screen with tv_id ON
Method = POST
"""
@power.route("/<tv_id>/screen_on", methods=['POST'])
def screen_on(tv_id):
    # setup client
    client = WebOSClient(load_ip(int(tv_id)))
    connect_client(client, load_store())
    system = SystemControl(client)

    system.screen_on()
    return {}
