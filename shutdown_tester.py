#! /usr/bin/env python3

import sys
import socket
import os
import struct

LASTCMD = ord('a')
TIMEOUT = 5

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

def main():
    if len(sys.argv) != 4:
        print(f"Usage:\n {sys.argv[0]} inactivity_time(>0) ListeningIP PORT")
        quit()

    #Get max inactivity time from args
    try:
        maxInactivity = int(sys.argv[1])
        IP = sys.argv[2]
        PORT = int(sys.argv[3])
    except ValueError as err:
        print(err)
        print(f"Usage:\n {sys.argv[0]} inactivity_time(>0) ListeningIP PORT")
        quit()
    
    #Create socket to communicate with server software on the same computer
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((IP,PORT))
    except ConnectionRefusedError as err:
        print ('Connection refused.')
        quit()
    
    sock.settimeout(TIMEOUT)
    dataRead = False
    try:
        writeSocket(sock, chr(LASTCMD).encode(encoding='utf-8'))
        data = readSocket(sock)
        if data[0] != LASTCMD:
            raise RuntimeError("Wrong command from server.")
        inactivityTime = int(data[1:].decode(encoding='utf-8'))
        dataRead = True
    except RuntimeError as err:
        print(err)
    except socket.timeout:
        print("Connection timed out.")
    except ValueError:
        print("Wrong payload from server")
    finally:
        sock.close()
    
    #shutdown machine
    if dataRead and inactivityTime >= maxInactivity:
        os.system("shutdown now")

if __name__ == "__main__":
    main()