#! /usr/bin/env python3

import socket
import struct
import signal
import os
from readWrite import *
PORT = 17568
BUF_SIZE = 64
working = True

def sigHandler(signo, frame):
    print(f"Signal {signo} caught.")

print("hello world")
signal.signal(signal.SIGUSR1, sigHandler)
print("server pid:", os.getpid())
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((socket.gethostname(), PORT))
sock.listen(5)

while working:
    print ("waiting for data...")
    
    try:
        (client_sock, address) = sock.accept()
        print("client accepted")
    except InterruptedError as e:
        print (e)
        print (e.__class__)
        continue
    except Exception as e:
        print (e)
        print (e.__class__)
        continue

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