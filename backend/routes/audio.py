from werkzeug.exceptions import BadRequest
from flask import Blueprint, request
from pywebostv.connection import WebOSClient
from db.storage import load_store
from helper import connect_client, load_ip
from pywebostv.controls import MediaControl

audio = Blueprint('audio', __name__, url_prefix='/smart')

"""
Raise the volume of tv with tv_id by 1
Method = POST
"""
@audio.route("/<tv_id>/raise_volume", methods=['POST'])
def raise_volume(tv_id):
    # setup client
    client = WebOSClient(load_ip(int(tv_id)))
    connect_client(client, load_store())
    media = MediaControl(client)

    media.volume_up()
    return {}

"""
Lower the volume of tv with tv_id by 1
Method = POST
"""
@audio.route("/<tv_id>/lower_volume", methods=['POST'])
def lower_volume(tv_id):
    # setup client
    client = WebOSClient(load_ip(int(tv_id)))
    connect_client(client, load_store())
    media = MediaControl(client)

    media.volume_down()
    return {}

"""
Set the volume of tv with tv_id to data['volume']
Volume must be integer from 0 to 100
Method = POST
"""
@audio.route("/<tv_id>/set_volume", methods=['POST'])
def set_volume(tv_id):
    # retrieve volume argument
    data = request.get_json()
    volume = data['volume']
    if volume < 0 or volume > 100:
        raise BadRequest('Volume out of range, must be 0-100')

    # setup client
    client = WebOSClient(load_ip(int(tv_id)))
    connect_client(client, load_store())
    media = MediaControl(client)

    # change volume
    media.set_volume(volume)
    if volume == 0:
        media.volume_down()
    return {}

"""
Toggle mute for tv with tv_id
Method = POST
"""
@audio.route("/<tv_id>/mute", methods=['POST'])
def toggle_mute(tv_id):
    # setup client
    client = WebOSClient(load_ip(int(tv_id)))
    connect_client(client, load_store())
    media = MediaControl(client)

    data = media.get_volume()
    status = data['volumeStatus']['muteStatus']
    media.mute(not status)
    return {'new_status' : not status}