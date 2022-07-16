import socket
import re
from urllib.parse import unquote
from time import sleep
from flask import Blueprint

def IRScan():
    request = b'M-SEARCH * HTTP/1.1\r\n' \
              b'HOST: 239.255.255.250:1900\r\n' \
              b'MAN: "ssdp:discover"\r\n' \
              b'MX: 10\r\n' \
              b'ST: ssdp:all\r\n\r\n'

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(request, (b'239.255.255.250', 1900))
    sock.settimeout(10)

    while True:
        response, address = sock.recvfrom(512)
        print(response.decode())
        print()

    sock.close()

IRScan()