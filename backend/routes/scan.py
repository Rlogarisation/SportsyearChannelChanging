import socket
import re
from urllib.parse import unquote
from time import sleep
from flask import Blueprint, request
from getmac import get_mac_address
from helper import scan_channels
from db.storage import persist_tv_data, load_tv_data
from werkzeug.exceptions import BadRequest

def LGTVScan():
    request = b'M-SEARCH * HTTP/1.1\r\n' \
              b'HOST: 239.255.255.250:1900\r\n' \
              b'MAN: "ssdp:discover"\r\n' \
              b'MX: 2\r\n' \
              b'ST: urn:schemas-upnp-org:device:MediaRenderer:1\r\n\r\n'

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(10)

    addresses = []
    attempts = 4
    for i in range(attempts):
        sock.sendto(request, (b'239.255.255.250', 1900))
        uuid = None
        tv_name = None
        address = None
        data = {}
        response, address = sock.recvfrom(512)
        for line in response.split(b'\n'):
            if line.startswith(b'USN'):
                try: 
                    uuid = re.findall(r'uuid:(.*?):', line.decode('utf-8'))[0]
                except:
                    data['usn'] = line.strip().decode('utf-8')
                    continue
            if line.startswith(b'DLNADeviceName.lge.com'):
                tv_name = unquote(
                    line.split(b':')[1].strip().decode('utf-8')
                )
        data = {
            'uuid': uuid,
            'tv_name': tv_name,
            'ip_address': address[0],
            'mac_address' : get_mac_address(ip=address[0])
        }

        if re.search(b'LG', response):
            addresses.append(data)
        else:
            print ('Unknown device')
            print (response, address)
        sleep(2)

    sock.close()

    addresses = list({x['uuid']: x for x in addresses}.values())

    # Reformat Addresses so we can index by uuid
    dict_addresses = {}
    for address in addresses:
        dict_addresses[address['uuid']] = {
            'tv_name' : address['tv_name'],
            'ip_address' : address['ip_address'],
            'mac_address' : address['mac_address']
        }
    return dict_addresses

# Setup blueprint for scan routes
scan = Blueprint('scan', __name__, url_prefix='/smart/')

def _remove_tv(uuid):
    data = load_tv_data()
    try:
        del data[uuid]
        persist_tv_data(data)
    except:
        raise BadRequest('UUID does not exist in Database')
    return {}

"""
Scan TV's, adding any extra TV's found to the existing list in the database
Returns the resultant list of TV Data in the database
Method = GET
"""
@scan.route("/scan", methods=['GET'])
def ScanTV():
    try:
        results = LGTVScan()
        current_data = load_tv_data()
        new_data = current_data.copy()
        update_ip = False

        for tv in results.keys():
            if tv not in current_data.keys():
                print(f'add tv [{tv}] to current ips')
                new_data[tv] = results[tv]
                update_ip = True
        if update_ip:
            persist_tv_data(new_data)

        for uuid in new_data:
            scan_channels(uuid)
        return {
            "scan" : load_tv_data()
        }

    except:
        raise BadRequest("No TV's were scanned")

"""
Remove tv with uuid from the database
Method = DEL
"""
@scan.route("/remove_tv", methods=['DELETE'])
def remove_tv():
    data = request.get_json()
    uuid = data['uuid']
    return _remove_tv(uuid)
