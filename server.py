#! /usr/bin/env python3

#Main server command loop

import socket

import xml_parsing
import configparser
import sockets

#configFile = '/etc/archvm_manager'
configFile = 'test.conf'

def handleCommands(sock, domainsList, config) -> None:
    working = True

    while working:
        #get data from request
        (client_sock, address) = sock.accept();
        try:
            data = sockets.readSocket(client_sock, int(config['CONSTANTS']['BUF_SIZE']))
        except ConnectionResetError as err:
            print("Connection from", address, "reset")
            continue
        except RuntimeError as err:
            print (err)
            continue

        if len(data) == 0:
            print("Wrong packet data")
            continue

        cmd = data[0]

        if cmd == sockets.CONNECT:
            connectHandle(data[1:], domainsList)
        elif cmd == sockets.DISCONNECT:
            disconnectHandle(data[1:], domainsList)
        elif cmd == sockets.HEARTBEAT:
            heartbeatHandle(data[1:], domainsList)
        elif cmd == sockets.REFRESH:
            #domainsList = updateDomainsStatus(domainsList)
            try:
                sockets.writeSocket(client_sock, (chr(sockets.REFRESH) + sockects.createXmlMessage(domainsList)).encode(encoding='utf-8'))
            except socket.timeout as err:
                print (f'Timeout exceeded when trying to send REFRESH data to', address[0])
        elif cmd == sockets.RELOAD:
            config.read(configFile)
            pass
        elif cmd == sockets.STOP:
            if sock.getsockname()[0] == address[0]:
                working = False
            else:
                print ("Wrong stop packet from", address, "data:", data)
        else:
            print ("Wrong packet from", address, "data:", data)

def main():
    config = configparser.ConfigParser()
    config.read(configFile)
    #domain_list = xml_parsing.importDomains(config['CONSTANTS']['VMS_XML_PATH'])
    #domainsList = domain_status.updateDomainsStatus(domainsList)
    domainsList = ''
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    p = int(config['CONSTANTS']['PORT'])
    a = socket.gethostname()
    sock.bind((socket.gethostname(), int(config['CONSTANTS']['PORT'])))
    sock.listen(5)

    handleCommands(sock, domainsList, config)

    sock.close()
    print("server down")



if __name__ == '__main__':
    main()