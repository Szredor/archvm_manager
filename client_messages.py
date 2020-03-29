#! /usr/bin/env python3

import subprocess
import socket

import sockets
import xml_parsing

TIMEOUT = 5

def printHelp() -> None:
    print("Type number of machine to connect with.")
    print("Type r to refresh list od domains.")
    print("Type \"exit\" to quit.")
    print("Type \"help\" or ? for this message.")

def printError(text) -> None:
    print (f'ERROR: {text}')

def connectMessage(name, address, port, bufSize) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((address,port))
    except ConnectionRefusedError as err:
        printError(f'Connection to {address} refused')
        return False
    
    sock.settimeout(TIMEOUT)
    try:
        sockets.writeSocket(sock, (chr(sockets.CONNECT) + name).encode(encoding='utf-8'))
        data = sockets.readSocket(sock, bufSize).decode(encoding='utf-8')
        if data[0] == sockets.ERROR:
            printError(data[1:])
            return False
        return True
    except socket.timeout:
        printError(f"Connection timed out")
        return False
    except ConnectionResetError as err:
        printError(f"Connection from {address} reset")
        return False
    except RuntimeError as err:
        printError (err)
        return False
    pass

def disconnectMessage(name, address, port, bufSize) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((address,port))
    except ConnectionRefusedError as err:
        printError(f'Connection to {address} refused')
        return False
    
    sock.settimeout(TIMEOUT)
    try:
        sockets.writeSocket(sock, (chr(sockets.DISCONNECT) + name).encode(encoding='utf-8'))
        data = sockets.readSocket(sock, bufSize).decode(encoding='utf-8')
        if data[0] == sockets.ERROR:
            printError(data[1:])
            return False
        return True
    except socket.timeout:
        printError(f"Connection timed out")
        return False
    except ConnectionResetError as err:
        printError(f"Connection from {address} reset")
        return False
    except RuntimeError as err:
        printError (err)
        return False
    pass

def heartbeatMessage(name, address, port, bufSize) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((address,port))
    except ConnectionRefusedError as err:
        return False
    
    sock.settimeout(TIMEOUT)
    try:
        sockets.writeSocket(sock, (chr(sockets.HEARTBEAT) + name).encode(encoding='utf-8'))
        data = sockets.readSocket(sock, bufSize).decode(encoding='utf-8')
        if data[0] == sockets.ERROR:
            printError(data[1:])
            return False 
        return True
    except socket.timeout:
        return False
    except ConnectionResetError as err:
        return False
    except RuntimeError as err:
        return False
    pass

def refreshMessage(address, port, bufSize) -> [xml_parsing.Domain]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((address,port))
    except ConnectionRefusedError as err:
        printError(f'Connection to {address} refused')
        return None
    
    sock.settimeout(TIMEOUT)
    try:
        sockets.writeSocket(sock, (chr(sockets.REFRESH)).encode(encoding='utf-8'))
        data = sockets.readSocket(sock, bufSize).decode(encoding='utf-8')
        return xml_parsing.importDomainsFromString(data[1:])
    except socket.timeout:
        printError(f"Connection timed out")
        return None
    except ConnectionResetError as err:
        printError(f"Connection from {address} reset")
        return None
    except RuntimeError as err:
        printError (err)
        return []
    pass

def runMoonlight(address, path):
    processStatus = subprocess.run([path])
    #processStatus = subprocess.run([path, 'stream', address, 'mstsc.exe'])
    #processStatus = subprocess.run([path, 'quit', 'address'])
    return processStatus.returncode

def runRDP(address, path):
    processStatus = subprocess.run([path, f'/v:{address}'])
    return processStatus.returncode