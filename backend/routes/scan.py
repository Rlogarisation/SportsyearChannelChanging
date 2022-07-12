import socket
import re
from urllib.parse import unquote
from time import sleep
from flask import Blueprint
from db.storage import persist_tv_ips, load_tv_ips
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
            'address': address[0]
        }

        if re.search(b'LG', response):
            addresses.append(data)
        else:
            print ('Unknown device')
            print (response, address)
        sleep(2)

    sock.close()
    addresses = list({x['uuid']: x for x in addresses}.values())
    return addresses

# Setup blueprint for scan routes
scan = Blueprint('scan', __name__, url_prefix='/smart')

"""
Retrieve list of tv's with their ip_address, tv_name & uuid
Method = GET
"""
@scan.route("/list", methods=['GET'])
def ScanTV():
    try:
        results = LGTVScan()
        current_ips = load_tv_ips()
        new_ips = current_ips.copy()
        update_ip = False
        for tv in results:
            if tv not in current_ips:
                print('add tv to current ips')
                new_ips.append(tv)
                update_ip = True
        if update_ip:
            persist_tv_ips(new_ips)
        return {
            "scan" : new_ips
        }

    except:
        raise BadRequest("No TV's were scanned")
