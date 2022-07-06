from flask import Blueprint, request
from pywebostv.connection import WebOSClient
from db.storage import load_store
from helper import connect_client, load_ip
from pywebostv.controls import SystemControl

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