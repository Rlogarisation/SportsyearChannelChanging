from db.storage import persist_store, load_tv_data, persist_tv_channels, load_store
from pywebostv.connection import WebOSClient
from werkzeug.exceptions import BadRequest
from pywebostv.controls import TvControl

def connect_client(client, uuid):
    client.connect()
    store = load_store(uuid)
    for status in client.register(store):
        if status == WebOSClient.PROMPTED:
            print("Please accept the connect on the TV!")
        elif status == WebOSClient.REGISTERED:
            print("Registration successful!")

    persist_store(store, uuid)

def load_ip(uuid):
    data = load_tv_data()

    try:
        ip = data[uuid]['ip_address']
    except:
        raise BadRequest("Provided UUID doesn't exist in database")

    return ip

def scan_channels(uuid):
    # setup client
    client = WebOSClient(load_ip(uuid))
    connect_client(client, uuid)
    tv_control = TvControl(client)

    list = tv_control.channel_list()
    tv_channels = {}

    for item in list['channelList']:
        tv_channels[item["channelNumber"]] = item["channelId"]
    persist_tv_channels(tv_channels, uuid)
    return tv_channels
