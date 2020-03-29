#! /usr/bin/env python3

#Main server command loop

import socket

import xml_parsing
import configparser
import sockets
import domain_status

#configFile = '/etc/archvm_manager'
configFile = 'test.conf'

def handleCommands(sock, domainList, config) -> None:
    working = True
    counter = 0

    while working:
        print("waiting for cmd...")
        #get data from request
        (client_sock, address) = sock.accept();
        try:
            data = sockets.readSocket(client_sock, int(config['COMMUNICATION']['BUF_SIZE']))
        except ConnectionResetError as err:
            print("Connection from", address, "reset")
            continue
        except RuntimeError as err:
            print (err)
            continue

        if len(data) == 0:
            print("Wrong packet data")
            continue

        client_sock.settimeout(5)
        cmd = data[0]

        #mark domain as occupied
        if cmd == sockets.CONNECT:           
            erText = domain_status.connectHandle(data[1:], domainList, client_sock, address[0])
            if not erText is None:
                sockets.sendError(client_sock, erText)
        #allow other users to occupy machine
        elif cmd == sockets.DISCONNECT:
            erText = domain_status.disconnectHandle(data[1:], domainList, client_sock, address[0])
            if not erText is None:
                sockets.sendError(client_sock, erText)
        #mark owner as alive
        elif cmd == sockets.HEARTBEAT:
            erText = domain_status.heartbeatHandle(data[1:], domainList, client_sock, address[0])
            if not erText is None:
                sockets.sendError(client_sock, erText)
        #refreshes state of domains and send it to client
        elif cmd == sockets.REFRESH:
            domain_status.updateDomainsStatus(domainList)
            try:
                sockets.writeSocket(client_sock, chr(sockets.REFRESH).encode(encoding='utf-8') + xml_parsing.createXmlMessage(domainList))
            except socket.timeout as err:
                print (f'Timeout exceeded when trying to send REFRESH data to', address[0])
        #reloads config file and imports domains from file
        elif cmd == sockets.RELOAD:
            if sock.getsockname()[0] == address[0]:
                config.read(configFile)
                temp = xml_parsing.importDomains(config['VIRTUALIZATION']['VMS_XML_PATH'])
                domain_status.changeToNewDomains(domainList, temp)
            else:
                print ("Wrong reload packet from", address, "data:", data)
        #stops server if and only if STOP command comes from server address
        elif cmd == sockets.STOP:
            if sock.getsockname()[0] == address[0]:
                working = False
            else:
                print ("Wrong stop packet from", address, "data:", data)
        else:
            print ("Wrong packet from", address, "data:", data)
        client_sock.close()

def main():
    config = configparser.ConfigParser()
    #defaultConfig(config)
    config.read(configFile)
    domainList = xml_parsing.importDomains(config['VIRTUALIZATION']['VMS_XML_PATH'])
    domain_status.prepareToWork(domainList, config)
    domain_status.updateDomainsStatus(domainList)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((config['COMMUNICATION']['IP'], int(config['COMMUNICATION']['PORT'])))
    sock.listen(5)

    handleCommands(sock, domainList, config)

    sock.close()
    domain_status.closeHypervisor()
    print("server down")

if __name__ == '__main__':
    main()