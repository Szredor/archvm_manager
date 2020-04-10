#! /usr/bin/env python3

import socket
import struct
from readWrite import *
PORT = 17568
BUF_SIZE = 64
working = True



print("hello world")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((socket.gethostname(), PORT))
sock.listen(5)

while working:
    print ("waiting for data...")
    (client_sock, address) = sock.accept();
    try:
        data = readSocket(client_sock, BUF_SIZE).decode(encoding = "utf-8")
    except ConnectionResetError as err:
        print("Connection from", address, "reset")
        continue
    except RuntimeError as err:
        print (err)
        continue

    if data == 'exit':
        working = False
    else:
        print (data)

sock.close()

print ("goodbye world")
print("press any key to continue...")
input()