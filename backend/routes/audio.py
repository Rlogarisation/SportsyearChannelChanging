from werkzeug.exceptions import BadRequest
from flask import Blueprint, request
from pywebostv.connection import WebOSClient
from db.storage import load_store
from helper import connect_client, load_ip
from pywebostv.controls import MediaControl

audio = Blueprint('audio', __name__, url_prefix='/smart/')

def _raise_volume(uuid):
    # setup client
    client = WebOSClient(load_ip(uuid))
    connect_client(client, uuid)
    media = MediaControl(client)

    media.volume_up()
    return {}

def _lower_volume(uuid):
    # setup client
    client = WebOSClient(load_ip(uuid))
    connect_client(client, uuid)
    media = MediaControl(client)

    media.volume_down()
    return {}

def _set_volume(volume, uuid):
    if volume < 0 or volume > 100:
        raise BadRequest('Volume out of range, must be 0-100')

    # setup client
    client = WebOSClient(load_ip(uuid))
    connect_client(client, uuid)
    media = MediaControl(client)

    # change volume
    media.set_volume(volume)
    if volume == 0:
        media.volume_down()
    return {}

def _toggle_mute(uuid):
    # setup client
    client = WebOSClient(load_ip(uuid))
    connect_client(client, uuid)
    media = MediaControl(client)

    data = media.get_volume()
    status = data['volumeStatus']['muteStatus']
    media.mute(not status)
    return {'new_status' : not status}

def _get_volume(uuid):
    # setup client
    client = WebOSClient(load_ip(uuid))
    connect_client(client, uuid)
    media = MediaControl(client)

    volume_data = media.get_volume()
    return {"volume_data" : volume_data}

"""
Raise the volume of tv with uuid by 1
Method = POST
"""
@audio.route("/raise_volume", methods=['POST'])
def raise_volume():
    data = request.get_json()
    uuid = data['uuid']
    return _raise_volume(uuid)

"""
Lower the volume of tv with uuid by 1
Method = POST
"""
@audio.route("/lower_volume", methods=['POST'])
def lower_volume():
    data = request.get_json()
    uuid = data['uuid']
    return _lower_volume(uuid)

"""
Set the volume of tv with uuid to data['volume']
Volume must be integer from 0 to 100
Method = POST
"""
@audio.route("/set_volume", methods=['POST'])
def set_volume():
    data = request.get_json()
    volume = data['volume']
    uuid = data['uuid']
    return _set_volume(volume, uuid)

"""
Toggle mute for tv with uuid
Method = POST
"""
@audio.route("/mute", methods=['POST'])
def toggle_mute():
    data = request.get_json()
    uuid = data['uuid']
    return _toggle_mute(uuid)

"""
Retreive current volume data from tv with uuid
Method = GET
"""
@audio.route("/get_volume", methods=['GET'])
def get_volume():
    data = request.get_json()
    uuid = data['uuid']
    return _get_volume(uuid)
