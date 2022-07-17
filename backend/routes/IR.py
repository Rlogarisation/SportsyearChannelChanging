from werkzeug.exceptions import BadRequest
from flask import Blueprint, request
from json import requests

IR = Blueprint('IR', __name__, url_prefix='/IR/')

"""
Send GET request to IR/test_ir
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
Send POST request to IR/test_ir
Body must include:
IP = ip number of arduino device
PORT = port number of arduino device
code = hexadecimal code or an array of int
passcode = passcode for sending requests
"""
@IR.route("/test_post_with_body")
def test_post_with_body():
    data = request.get_json()
    IP = data['IP']
    PORT = data['PORT']

    # IR code such as A90:SONY:12
    code = data['code']
    # Passcode required to execute IR command
    passcode = data['passcode']

    URL = f'http://{IP}:{PORT}/msg?pass={passcode}'
    myobj = {
        "type":"lg",
        "data": code,
        "length":32 # bit length
    }

    r = requests.post(URL, myobj)
    data = r.json()
    print(data)
    return {
        'data' : data
    }