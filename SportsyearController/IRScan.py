import socket
import re
from urllib.parse import unquote
from time import sleep
from flask import Blueprint

def IRScan():
    SSDP_DISCOVER = ('M-SEARCH * HTTP/1.1\r\n' +
                        'HOST: 239.255.255.250:1900\r\n' +
                        'MAN: "ssdp:discover"\r\n' +
                        'MX: 10\r\n' +
                        'ST: ssdp:all\r\n\r\n')
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