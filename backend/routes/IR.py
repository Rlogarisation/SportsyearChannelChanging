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
        return devices

"""
Send GET request to ir/test_ir
Body must include:
IP = ip number of arduino device
PORT = port number of arduino device
code = hexadecimal code or an array of int
passcode = passcode for sending requests
"""
@IR.route("/scan", methods=['GET'])
def test_ir():
    try:
        ir_device_list = IRScan()
        current_data = ir_load_blaster_data()
        new_data = current_data.copy()
        updated = False

        for device in ir_device_list:
            if device not in current_data:
                print(f'Adding [{device[0]}] with location [{device[1]}:{device[2]}] to database')
                new_data.append(device)
                updated = True
        if updated:
            ir_persist_blaster_data(new_data)
        return {
            "scan" : ir_load_blaster_data
        }
    except:
        raise BadRequest("No blasters were scanned")

"""
Send POST request to ir/set_channel
Body must include:
IP = ip number of arduino device
PORT = port number of arduino device
CHANNEL = channel to change to
TYPE = tv type
LENGTH = length of code to be sent
"""
@IR.route("/set_channel", methods=['POST'])
def test_post_with_body():
    data = request.get_json()
    IP = data['IP']
    PORT = data['PORT']
    CHANNEL = data['CHANNEL']
    TYPE = data['TYPE']
    LENGTH = data['LENGTH']

    URL = f'http://{IP}:{PORT}/ir/set_channel?channel={CHANNEL}&type={TYPE}&length={LENGTH}'
    myobj = {
        "channel" : data['CHANNEL'],
        "type" : data['TYPE'],
        "length" : data['LENGTH'],
    }

    r = requests.post(URL, myobj)
    data = r.json()
    print(data)
    return {
        'data' : data
    }


"""
Send POST request to ir/lower_volume
Body must include:
IP = ip number of arduino device
PORT = port number of arduino device
TYPE = tv type
LENGTH = length of code to be sent
"""
@IR.route("/lower_volume", methods=['POST'])
def lower_volume():
    data = request.get_json()
    IP = data['IP']
    PORT = data['PORT']
    TYPE = data['TYPE']
    LENGTH = data['LENGTH']

    URL = f'http://{IP}:{PORT}/ir/lower_volume?type={TYPE}&length={LENGTH}'
    myobj = {
        "type" : data['TYPE'],
        "length" : data['LENGTH'],
    }

    r = requests.post(URL, myobj)
    data = r.json()
    print(data)
    return {
        'data' : data
    }

"""
Send POST request to ir/raise_volume
Body must include:
IP = ip number of arduino device
PORT = port number of arduino device
TYPE = tv type
LENGTH = length of code to be sent
"""
@IR.route("/raise_volume", methods=['POST'])
def raise_volume():
    data = request.get_json()
    IP = data['IP']
    PORT = data['PORT']
    TYPE = data['TYPE']
    LENGTH = data['LENGTH']

    URL = f'http://{IP}:{PORT}/ir/raise_volume?type={TYPE}&length={LENGTH}'
    myobj = {
        "type" : data['TYPE'],
        "length" : data['LENGTH'],
    }

    r = requests.post(URL, myobj)
    data = r.json()
    print(data)
    return {
        'data' : data
    }

"""
Send POST request to ir/mute
Body must include:
IP = ip number of arduino device
PORT = port number of arduino device
TYPE = tv type
LENGTH = length of code to be sent
"""
@IR.route("/mute", methods=['POST'])
def mute():
    data = request.get_json()
    IP = data['IP']
    PORT = data['PORT']
    TYPE = data['TYPE']
    LENGTH = data['LENGTH']

    URL = f'http://{IP}:{PORT}/ir/mute?type={TYPE}&length={LENGTH}'
    myobj = {
        "type" : data['TYPE'],
        "length" : data['LENGTH'],
    }

    r = requests.post(URL, myobj)
    data = r.json()
    print(data)
    return {
        'data' : data
    }

"""
Send POST request to ir/power
Body must include:
IP = ip number of arduino device
PORT = port number of arduino device
TYPE = tv type
LENGTH = length of code to be sent
"""
@IR.route("/power", methods=['POST'])
def power():
    data = request.get_json()
    IP = data['IP']
    PORT = data['PORT']
    TYPE = data['TYPE']
    LENGTH = data['LENGTH']

    URL = f'http://{IP}:{PORT}/ir/power?type={TYPE}&length={LENGTH}'
    myobj = {
        "type" : data['TYPE'],
        "length" : data['LENGTH'],
    }

    r = requests.post(URL, myobj)
    data = r.json()
    print(data)
    return {
        'data' : data
    }

"""
Send POST request to ir/raise_channel
Body must include:
IP = ip number of arduino device
PORT = port number of arduino device
TYPE = tv type
LENGTH = length of code to be sent
"""
@IR.route("/raise_channel", methods=['POST'])
def raise_channel():
    data = request.get_json()
    IP = data['IP']
    PORT = data['PORT']
    TYPE = data['TYPE']
    LENGTH = data['LENGTH']

    URL = f'http://{IP}:{PORT}/ir/raise_channel?type={TYPE}&length={LENGTH}'
    myobj = {
        "type" : data['TYPE'],
        "length" : data['LENGTH'],
    }

    r = requests.post(URL, myobj)
    data = r.json()
    print(data)
    return {
        'data' : data
    }

"""
Send POST request to ir/lower_channel
Body must include:
IP = ip number of arduino device
PORT = port number of arduino device
TYPE = tv type
LENGTH = length of code to be sent
"""
@IR.route("/lower_channel", methods=['POST'])
def lower_channel():
    data = request.get_json()
    IP = data['IP']
    PORT = data['PORT']
    TYPE = data['TYPE']
    LENGTH = data['LENGTH']

    URL = f'http://{IP}:{PORT}/ir/lower_channel?type={TYPE}&length={LENGTH}'
    myobj = {
        "type" : data['TYPE'],
        "length" : data['LENGTH'],
    }

    r = requests.post(URL, myobj)
    data = r.json()
    print(data)
    return {
        'data' : data
    }