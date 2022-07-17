from werkzeug.exceptions import BadRequest
from flask import Blueprint, request
import requests

IR = Blueprint('IR', __name__, url_prefix='/ir/')

"""
Send GET request to ir/test_ir
Body must include:
IP = ip number of arduino device
PORT = port number of arduino device
code = hexadecimal code or an array of int
passcode = passcode for sending requests
"""
@IR.route("/test_ir", methods=['GET'])
def test_ir():
    data = request.get_json()
    IP = data['IP']
    PORT = data['PORT']

    # IR code such as A90:SONY:12
    code = data['code']
    # Passcode required to execute IR command
    passcode = data['passcode']

    URL = f'http://{IP}:{PORT}/msg?code={code}&pass={passcode}'
    # r = requests.post(url = URL)
    r = requests.get(url = URL)
    data = r.json()
    print(data)
    return {
        'data' : data
    }

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