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
LASTCMD = ord('a')

def readSocket(sock, bufSize = 1024) -> b'':
    #get size of payload
    bytes_length = sock.recv(4)
    msgsize = struct.unpack('!I', bytes_length)[0]
    received = 0
    chunks = []

    #Read data in chunks until whole message pass
    while received < msgsize:
        try:
            chunk = sock.recv(min(bufSize, msgsize - received))
        ex
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

def sendError(sock, text) -> None:
    payload = (chr(ERROR) + text).encode(encoding='utf-8')
    try:
        writeSocket(sock, payload)
    except socket.timeout as err:
        pass
    pass

#source: https://stackoverflow.com/questions/28765352/wakeup-on-lan-with-python
#wakeonlan magic packet creation
def WakeOnLan(ethernet_address, broadcast, port):
    cmd = "lol"
    while cmd != 'y' and cmd != 'Y' and cmd != 'n' and cmd != 'N' and cmd != '':
        print("Do you want to send WakeOnLan to server?[Y/n] ", end="")
        cmd = input()
    if cmd == 'n' or cmd == 'N':
        return
     
    add_oct = []
    if len(ethernet_address) < 11:
        raise ValueError("MAC address is in wrong format. Check config file.")

    # Construct 6 byte hardware address
    add_oct = ethernet_address.split(':')
    if len(add_oct) != 6:
        add_oct = ethernet_address.split('-')
    if len(add_oct) != 6:
        add_oct.clear()
        for i in range(0,6):
            add_oct.append(ethernet_address[2*i:2*(i+1)])
    if len(add_oct) != 6:
        raise ValueError("MAC address is in wrong format. Check config file.")

    hwa = struct.pack('!BBBBBB', int(add_oct[0],16),
        int(add_oct[1],16),
        int(add_oct[2],16),
        int(add_oct[3],16),
        int(add_oct[4],16),
        int(add_oct[5],16))

    # Build magic packet
    msg = b'\xff' * 6 + hwa * 16

    # Send packet to broadcast address using UDP port 9
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
    soc.sendto(msg,(broadcast, port))
    soc.close()