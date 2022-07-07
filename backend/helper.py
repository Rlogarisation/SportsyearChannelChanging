from db.storage import persist_store, load_tv_ips, persist_tv_channels, load_store
from pywebostv.connection import WebOSClient
from werkzeug.exceptions import BadRequest
from pywebostv.controls import TvControl

def connect_client(client, store):
    client.connect()
    for status in client.register(store):
        if status == WebOSClient.PROMPTED:
            print("Please accept the connect on the TV!")
        elif status == WebOSClient.REGISTERED:
            print("Registration successful!")

    persist_store(store)

def load_ip(tv_num):
    if tv_num >= len(load_tv_ips()) or tv_num < 0 :
        raise BadRequest('tv_id out of range')

    return str(load_tv_ips()[tv_num]['address'])

def load_mac(tv_num):
    if tv_num >= len(load_tv_ips()) or tv_num < 0 :
        raise BadRequest('tv_id out of range')

    return str(load_tv_ips()[tv_num]['mac'])

def scan_channels(tv_id):
    # setup client
    client = WebOSClient(load_ip(int(tv_id)))
    connect_client(client, load_store())
    tv_control = TvControl(client)

    list = tv_control.channel_list()
    tv_channels = {}

    for item in list['channelList']:
        tv_channels[item["channelNumber"]] = item["channelId"]
    persist_tv_channels(tv_channels)
    return tv_channels
