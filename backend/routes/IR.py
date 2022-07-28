from werkzeug.exceptions import BadRequest
from flask import Blueprint, request
from db.storage import ir_persist_blaster_data, ir_load_blaster_data
import requests
import socket

IR = Blueprint('IR', __name__, url_prefix='/ir/')

def IRScan():
    SSDP_DISCOVER = ('M-SEARCH * HTTP/1.1\r\n' +
                        'HOST: 239.255.255.250:1900\r\n' +
                        'MAN: "ssdp:discover"\r\n' +
                        'MX: 10\r\n' +
                        'ST: upnp:rootdevice\r\n\r\n')
    BCAST_IP = '239.255.255.250'
    BCAST_PORT = 1900
    LINES_IN_RESPONSE = 9
    devices = []
    found_devices_list = []
    return_dict = {}
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(10)
        sock.sendto(SSDP_DISCOVER.encode('ASCII'), (BCAST_IP, BCAST_PORT))
        while True:
            response, _ = sock.recvfrom(1024)
            response = response.decode().split('\n')
            if len(response) == LINES_IN_RESPONSE:
                if "arduino" in response[3].lower():
                    address = response[6].split(' ')[1].split('/')[2]
                    if address not in found_devices_list:
                        tv_name = response[3].split(' ')[4].split('/')[0]
                        blaster_hostname = address.split(':')[0]
                        blaster_port = address.split(':')[1]
                        devices.append((tv_name,blaster_hostname,blaster_port))
                        found_devices_list.append(address)
    except:
        sock.close()
        for device in devices:
            return_dict[device[0]] = {"ip_address":device[1], "port":device[2], "type":"NEC"}
        return return_dict

def _ir_set_channel(IP, PORT, CHANNEL, TYPE):
    URL = f'http://{IP}:{PORT}/ir/set_channel?channel={CHANNEL}&type={TYPE}'
    try:
        requests.post(URL)
    except requests.exceptions.ChunkedEncodingError:
        return {}
    return {}

def _ir_lower_volume(IP, PORT, TYPE):
    URL = f'http://{IP}:{PORT}/ir/lower_volume?type={TYPE}'
    try:
        requests.post(URL)
    except requests.exceptions.ChunkedEncodingError:
        return {}
    return {}

def _ir_raise_volume(IP, PORT, TYPE):
    URL = f'http://{IP}:{PORT}/ir/raise_volume?type={TYPE}'
    try:
        requests.post(URL)
    except requests.exceptions.ChunkedEncodingError:
        return {}
    return {}

def _ir_mute(IP, PORT, TYPE):
    URL = f'http://{IP}:{PORT}/ir/mute?type={TYPE}'
    try:
        requests.post(URL)
    except requests.exceptions.ChunkedEncodingError:
        return {}
    return {}

def _ir_power(IP, PORT, TYPE):
    URL = f'http://{IP}:{PORT}/ir/power?type={TYPE}'
    try:
        requests.post(URL)
    except requests.exceptions.ChunkedEncodingError:
        return {}
    return {}

def _ir_raise_channel(IP, PORT, TYPE):
    URL = f'http://{IP}:{PORT}/ir/raise_channel?type={TYPE}'
    try:
        requests.post(URL)
    except requests.exceptions.ChunkedEncodingError:
        return {}
    return {}

def _ir_lower_channel(IP, PORT, TYPE):
    URL = f'http://{IP}:{PORT}/ir/lower_channel?type={TYPE}'
    try:
        requests.post(URL)
    except requests.exceptions.ChunkedEncodingError:
        return {}
    return {}

"""
Send GET request to ir/scan
No Body is needed
Returns a dictionary:
Device_name: { "ip_address":<>, "port":<> }
"""
@IR.route("/scan", methods=['GET'])
def ir_scan():
    try:
        ir_device_list = IRScan()
        current_data = ir_load_blaster_data()
        new_data = current_data.copy()
        updated = False
        for device in ir_device_list.keys():
            if device not in current_data.keys():
                print(f'Adding [{device}] with location [{ir_device_list[device]["ip_address"]}:{ir_device_list[device]["port"]}] to database')
                new_data[device] = ir_device_list[device]
                updated = True
        if updated:
            ir_persist_blaster_data(new_data)
        return {
            "scan" : ir_load_blaster_data()
        }
    except:
        raise BadRequest("No blasters were scanned")

"""
Send POST request to ir/brand
Body must include:
Device_name = name of the device as obtained from the database
Type = the brand of the TV as selected from a dropdown
"""
@IR.route("/brand", methods=['POST'])
def ir_brand():
    data = request.get_json()
    DEVICE_NAME = data['DEVICE_NAME']
    TYPE = data['TYPE']
    current_data = ir_load_blaster_data()
    current_data[DEVICE_NAME]['type'] = TYPE
    ir_persist_blaster_data(current_data)
    return {}


"""
Send POST request to ir/set_channel
Body must include:
IP = ip number of arduino device
PORT = port number of arduino device
CHANNEL = channel to change to
TYPE = tv type
"""
@IR.route("/set_channel", methods=['POST'])
def ir_set_channel():
    data = request.get_json()
    DEVICE_NAME = data['DEVICE_NAME']
    CHANNEL = data['CHANNEL']

    db = ir_load_blaster_data()
    this_blaster = db[DEVICE_NAME]

    IP = this_blaster['ip_address']
    PORT = this_blaster['port']
    TYPE = this_blaster['type']
    return _ir_set_channel(IP, PORT, CHANNEL, TYPE)


"""
Send POST request to ir/lower_volume
Body must include:
IP = ip number of arduino device
PORT = port number of arduino device
TYPE = tv type
"""
@IR.route("/lower_volume", methods=['POST'])
def ir_lower_volume():
    data = request.get_json()
    DEVICE_NAME = data['DEVICE_NAME']

    db = ir_load_blaster_data()
    this_blaster = db[DEVICE_NAME]

    IP = this_blaster['ip_address']
    PORT = this_blaster['port']
    TYPE = this_blaster['type']
    return _ir_lower_volume(IP, PORT, TYPE)

"""
Send POST request to ir/raise_volume
Body must include:
IP = ip number of arduino device
PORT = port number of arduino device
TYPE = tv type
"""
@IR.route("/raise_volume", methods=['POST'])
def ir_raise_volume():
    data = request.get_json()
    DEVICE_NAME = data['DEVICE_NAME']

    db = ir_load_blaster_data()
    this_blaster = db[DEVICE_NAME]

    IP = this_blaster['ip_address']
    PORT = this_blaster['port']
    TYPE = this_blaster['type']
    return _ir_raise_volume(IP, PORT, TYPE)

"""
Send POST request to ir/mute
Body must include:
IP = ip number of arduino device
PORT = port number of arduino device
TYPE = tv type
"""
@IR.route("/mute", methods=['POST'])
def ir_mute():
    data = request.get_json()
    DEVICE_NAME = data['DEVICE_NAME']

    db = ir_load_blaster_data()
    this_blaster = db[DEVICE_NAME]

    IP = this_blaster['ip_address']
    PORT = this_blaster['port']
    TYPE = this_blaster['type']
    return _ir_mute(IP, PORT, TYPE)

"""
Send POST request to ir/power
Body must include:
IP = ip number of arduino device
PORT = port number of arduino device
TYPE = tv type
"""
@IR.route("/power", methods=['POST'])
def ir_power():
    data = request.get_json()
    DEVICE_NAME = data['DEVICE_NAME']

    db = ir_load_blaster_data()
    this_blaster = db[DEVICE_NAME]

    IP = this_blaster['ip_address']
    PORT = this_blaster['port']
    TYPE = this_blaster['type']
    return _ir_power(IP, PORT, TYPE)

"""
Send POST request to ir/raise_channel
Body must include:
IP = ip number of arduino device
PORT = port number of arduino device
TYPE = tv type
"""
@IR.route("/raise_channel", methods=['POST'])
def ir_raise_channel():
    data = request.get_json()
    DEVICE_NAME = data['DEVICE_NAME']

    db = ir_load_blaster_data()
    this_blaster = db[DEVICE_NAME]

    IP = this_blaster['ip_address']
    PORT = this_blaster['port']
    TYPE = this_blaster['type']
    return _ir_raise_channel(IP, PORT, TYPE)

"""
Send POST request to ir/lower_channel
Body must include:
IP = ip number of arduino device
PORT = port number of arduino device
TYPE = tv type
"""
@IR.route("/lower_channel", methods=['POST'])
def ir_lower_channel():
    data = request.get_json()
    DEVICE_NAME = data['DEVICE_NAME']

    db = ir_load_blaster_data()
    this_blaster = db[DEVICE_NAME]

    IP = this_blaster['ip_address']
    PORT = this_blaster['port']
    TYPE = this_blaster['type']
    return _ir_lower_channel(IP, PORT, TYPE)

"""
Returns the list of IR Remotes in the database
Method = GET
"""
@IR.route("/get_remotes", methods=['GET'])
def get_remotes():
    try:
        current_data = ir_load_blaster_data()
        return {
            "ir_remotes" : current_data
        }

    except:
        raise BadRequest("No TV's exist in Database")
