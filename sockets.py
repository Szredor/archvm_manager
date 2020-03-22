#! /usr/bin/env python3

#Group of functions to communicate

import socket
import struct

CONNECT = ord('c')
DISCONNECT = ord('d')
ERROR = ord('e')
HEARTBEAT = ord('h')
REFRESH = ord('r')
RELOAD = ord('l')
STOP = ord('s')

def readSocket(sock, bufSize = 1024) -> b'':
    #get size of payload
    bytes_length = sock.recv(4)
    msgsize = struct.unpack('!I', bytes_length)[0]
    received = 0
    chunks = []

    #Read data in chunks until whole message pass
    while received < msgsize:
        chunk = sock.recv(min(bufSize, msgsize - received))
        if chunk == b'':
            raise RuntimeError('Socket connection broken')
        chunks.append(chunk)
        received += len(chunk)
    
    #Check length of payload and return data
    if (not received == msgsize):
        raise RuntimeError('Message size incorrect')

    return b''.join(chunks)

def writeSocket(sock, data) -> int:
    msgsize = len(data)
    payload = struct.pack('!I', msgsize) + data
    #send all data to other side
    sock.sendall(payload)
    return msgsize







