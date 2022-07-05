from db.storage import persist_store, load_tv_ips
from pywebostv.connection import WebOSClient
from werkzeug.exceptions import BadRequest

def connect_client(client, store):
    client.connect()
    for status in client.register(store):
        if status == WebOSClient.PROMPTED:
            print("Please accept the connect on the TV!")
        elif status == WebOSClient.REGISTERED:
            print("Registration successful!")

    persist_store(store)

def load_ip(ip_num):
    if ip_num >= len(load_tv_ips()['scan']) or ip_num < 0 :
        raise BadRequest('tv_id out of range')

    return str(load_tv_ips()['scan'][ip_num]['address'])