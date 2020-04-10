#! /usr/bin/env python3

import socket
from readWrite import *

IP = "192.168.0.146"
PORT = 17568
BUF_SIZE = 64
data = ''

while True:
    print("type data to send")
    data = input();
    if data == 'stop':
        break

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((IP,PORT))
    except ConnectionRefusedError as err:
        print ('Connection refused')
        quit()
    
    sock.settimeout(0.5)
    writeSocket(sock, data.encode(encoding='utf-8'))
    sock.close()

print("goodbye world")
#print("press any key to continue...")
#input()
