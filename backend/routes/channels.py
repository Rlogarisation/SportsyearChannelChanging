from werkzeug.exceptions import BadRequest
from flask import Blueprint, request
from pywebostv.connection import WebOSClient
from db.storage import load_store, load_tv_channels
from helper import connect_client, load_ip
from pywebostv.controls import TvControl

channels = Blueprint('channels', __name__, url_prefix='/smart/<uuid>/')

"""
Set tv with uuid to channel with data['channel_id']
Method = POST
"""
@channels.route("/set_channel", methods=['POST'])
def set_channel(uuid):
    # retrieve volume argument
    data = request.get_json()
    channel_id = data['channel_id']
    channel_list = load_tv_channels(uuid)

    if channel_id not in channel_list.keys():
        raise BadRequest('{channel_id} not in list of channels for tv {uuid}')

    # setup client
    client = WebOSClient(load_ip(uuid))
    connect_client(client, uuid)
    tv_control = TvControl(client)

    tv_control.set_channel_with_id(channel_list[channel_id])
    return {}

"""
Change channel up 1 for tv with uuid
Method = POST
"""
@channels.route("/raise_channel", methods=['POST'])
def raise_channel(uuid):
    # setup client
    client = WebOSClient(load_ip(uuid))
    connect_client(client, uuid)
    tv_control = TvControl(client)

    tv_control.channel_up()
    return {}

"""
Change channel down 1 for tv with uuid
Method = POST
"""
@channels.route("/lower_channel", methods=['POST'])
def lower_channel(uuid):
    # setup client
    client = WebOSClient(load_ip(uuid))
    connect_client(client, uuid)
    tv_control = TvControl(client)

    tv_control.channel_down()
    return {}

"""
Retrieve channel list for tv with uuid
Method = POST
"""
@channels.route("/channel_list", methods=['GET'])
def channel_list(uuid):
    # setup client
    client = WebOSClient(load_ip(uuid))
    connect_client(client, uuid)
    tv_control = TvControl(client)

    list = tv_control.channel_list()
    return {"list" : list}
