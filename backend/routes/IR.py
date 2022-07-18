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
            return_dict[device[0]] = {"ip_address":device[1], "port":device[2]}
        return return_dict

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
        print(ir_device_list)
        for device in ir_device_list.keys():
            if device not in current_data.keys():
                print(f'Adding [{device}] with location [{device["ip_address"]}:{device["port"]}] to database')
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
Send POST request to ir/set_channel
Body must include:
IP = ip number of arduino device
PORT = port number of arduino device
CHANNEL = channel to change to
TYPE = tv type
LENGTH = length of code to be sent
"""
@IR.route("/set_channel", methods=['POST'])
def ir_set_channel():
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

    requests.post(URL, myobj)
    return {}


"""
Send POST request to ir/lower_volume
Body must include:
IP = ip number of arduino device
PORT = port number of arduino device
TYPE = tv type
LENGTH = length of code to be sent
"""
@IR.route("/lower_volume", methods=['POST'])
def ir_lower_volume():
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

    requests.post(URL, myobj)
    return {}

"""
Send POST request to ir/raise_volume
Body must include:
IP = ip number of arduino device
PORT = port number of arduino device
TYPE = tv type
LENGTH = length of code to be sent
"""
@IR.route("/raise_volume", methods=['POST'])
def ir_raise_volume():
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

    requests.post(URL, myobj)
    return {}

"""
Send POST request to ir/mute
Body must include:
IP = ip number of arduino device
PORT = port number of arduino device
TYPE = tv type
LENGTH = length of code to be sent
"""
@IR.route("/mute", methods=['POST'])
def ir_mute():
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

    requests.post(URL, myobj)
    return {}

"""
Send POST request to ir/power
Body must include:
IP = ip number of arduino device
PORT = port number of arduino device
TYPE = tv type
LENGTH = length of code to be sent
"""
@IR.route("/power", methods=['POST'])
def ir_power():
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

    requests.post(URL, myobj)
    return {}

"""
Send POST request to ir/raise_channel
Body must include:
IP = ip number of arduino device
PORT = port number of arduino device
TYPE = tv type
LENGTH = length of code to be sent
"""
@IR.route("/raise_channel", methods=['POST'])
def ir_raise_channel():
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

    requests.post(URL, myobj)
    return {}

"""
Send POST request to ir/lower_channel
Body must include:
IP = ip number of arduino device
PORT = port number of arduino device
TYPE = tv type
LENGTH = length of code to be sent
"""
@IR.route("/lower_channel", methods=['POST'])
def ir_lower_channel():
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

    requests.post(URL, myobj)
    return {}