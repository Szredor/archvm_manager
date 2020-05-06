#! /usr/bin/env python3

import subprocess
import socket
import sys
import os
sys.path.append("./common")

import sockets
import xml_parsing

def printHelp() -> None:
    print("Type number of machine to connect with.")
    print("Type r to refresh list od domains.")
    print("Type \"exit\" to quit.")
    print("Type \"help\" or ? for this message.")

def printError(text) -> None:
    print (f'ERROR: {text}')

def connectMessage(name, address, port, bufSize) -> bool:
    sock = sockets.create_connected_socket(address, port)
    if sock is None:
        return False
    
    result = True
    try:
        sockets.writeSocket(sock, (chr(sockets.CONNECT) + name).encode(encoding='utf-8'))
        data = sockets.readSocket(sock, bufSize).decode(encoding='utf-8')
        if data[0] == sockets.ERROR:
            printError(data[1:])
            result = False
    except socket.timeout:
        printError(f"Connection timed out")
        result = False
    except ConnectionResetError as err:
        printError(f"Connection from {address} reset")
        result = False
    except RuntimeError as err:
        printError (err)
        result = False
    finally:
        sock.close()
    return result

def disconnectMessage(name, address, port, bufSize) -> bool:
    sock = sockets.create_connected_socket(address, port)
    if sock is None:
        return False
    
    result = True
    try:
        sockets.writeSocket(sock, (chr(sockets.DISCONNECT) + name).encode(encoding='utf-8'))
        data = sockets.readSocket(sock, bufSize).decode(encoding='utf-8')
        if data[0] == sockets.ERROR:
            printError(data[1:])
            result = False
    except socket.timeout:
        printError(f"Connection timed out")
        result = False
    except ConnectionResetError as err:
        printError(f"Connection from {address} reset")
        result = False
    except RuntimeError as err:
        printError (err)
        result = False
    finally:
        sock.close()
    return result

def heartbeatMessage(name, address, port, bufSize) -> bool:
    sock = sockets.create_connected_socket(address, port)
    if sock is None:
        return False
    
    result = True
    try:
        sockets.writeSocket(sock, (chr(sockets.HEARTBEAT) + name).encode(encoding='utf-8'))
        data = sockets.readSocket(sock, bufSize).decode(encoding='utf-8')
        if data[0] == sockets.ERROR:
            printError(data[1:])
            result = False 
    except socket.timeout:
        result = False
    except ConnectionResetError as err:
        result = False
    except RuntimeError as err:
        result = False
    finally:
        sock.close()
    return result

def refreshMessage(address, port, bufSize) -> [xml_parsing.Domain]:
    sock = sockets.create_connected_socket(address, port)
    if sock is None:
        return None
    
    result = None
    try:
        sockets.writeSocket(sock, (chr(sockets.REFRESH)).encode(encoding='utf-8'))
        data = sockets.readSocket(sock, bufSize).decode(encoding='utf-8')
        result = xml_parsing.importDomainsFromString(data[1:])
    except socket.timeout:
        printError(f"Connection timed out")
    except ConnectionResetError as err:
        printError(f"Connection from {address} reset")
    except RuntimeError as err:
        printError (err)
        result = []
    finally:
        sock.close()
    return result

def runMoonlight(address, path) -> int:
    processStatus = os.system(path)
    #processStatus = subprocess.run([path, 'stream', address, 'mstsc.exe'])
    #processStatus = subprocess.run([path, 'quit', 'address'])
    return processStatus

def runRDP(address, path) -> int:
    processStatus = os.system(f'{path} /v:{address}')
    return processStatus