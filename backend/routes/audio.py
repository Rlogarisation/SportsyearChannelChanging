from werkzeug.exceptions import BadRequest
from flask import Blueprint, request
from pywebostv.connection import WebOSClient
from db.storage import load_store
from helper import connect_client, load_ip
from pywebostv.controls import MediaControl

audio = Blueprint('audio', __name__, url_prefix='/smart/<uuid>/')

"""
Raise the volume of tv with uuid by 1
Method = POST
"""
@audio.route("/raise_volume", methods=['POST'])
def raise_volume(uuid):
    # setup client
    client = WebOSClient(load_ip(uuid))
    connect_client(client, uuid)
    media = MediaControl(client)

    media.volume_up()
    return {}

"""
Lower the volume of tv with uuid by 1
Method = POST
"""
@audio.route("/lower_volume", methods=['POST'])
def lower_volume(uuid):
    # setup client
    client = WebOSClient(load_ip(uuid))
    connect_client(client, uuid)
    media = MediaControl(client)

    media.volume_down()
    return {}

"""
Set the volume of tv with uuid to data['volume']
Volume must be integer from 0 to 100
Method = POST
"""
@audio.route("/set_volume", methods=['POST'])
def set_volume(uuid):
    # retrieve volume argument
    data = request.get_json()
    volume = data['volume']
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

"""
Mute tv with uuid
Status = "True" for mute
Status = "False" for unmute
Method = POST
"""
@audio.route("/mute", methods=['POST'])
def mute(uuid):
    # retrieve mute status argument
    data = request.get_json()
    status = data['status']

    if status != 'True' and status != 'False':
        raise BadRequest('Status should be "True" or "False"')

    # setup client
    client = WebOSClient(load_ip(uuid))
    connect_client(client, uuid)
    media = MediaControl(client)

    media.mute(status == 'True')
    return {}