#! /usr/bin/env python3

#Main server command loop

import socket
import signal
import time
import sys
sys.path.append("common")

import xml_parsing
import configparser
import sockets
import domain_status

#configFile = '/etc/archvm_manager'
configFile = 'test.conf'

def handleCommands(sock, domainList, config) -> None:
    def stopHandler(signum, frame):
        sock.close()
        try:
            client_sock.close()
        except OSError:
            pass
        domain_status.closeHypervisor()
        print("server down")
        quit()

    working = True
    counter = 0
    lastCmd = time.clock()

    signal.signal(signal.SIGTERM, stopHandler)
    while working:
        #print("waiting for cmd...")
        #get data from request
        try:
            (client_sock, address) = sock.accept()
        except InterruptedError:
            continue

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
            client_sock.close()
            continue

        client_sock.settimeout(5)
        cmd = data[0]

        #return full minutes from last command
        if cmd == sockets.LASTCMD and sock.getsockname()[0] == address[0]:
            now = time.clock()
            absenceMinutes = int((now - lastCmd)/60)
            try:
                sockets.writeSocket(client_sock, (chr(sockets.LASTCMD) + absenceMinutes).encode("utf-8"))
            except socket.timeout as err:
                print (f'Timeout exceeded when trying to send LASTCMD data to', address[0])
            client_sock.close()
            continue

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
        lastCmd = time.clock()


def main():
    def reloadHandler(signum, frame):
        config.read(configFile)
        temp = xml_parsing.importDomains(config['VIRTUALIZATION']['VMS_XML_PATH'])
        domain_status.changeToNewDomains(domainList, temp)

    signal.signal(signal.SIGHUP, reloadHandler)
    config = configparser.ConfigParser()
    #defaultConfig(config)
    config.read(configFile)
    domainList = xml_parsing.importDomains(config['VIRTUALIZATION']['VMS_XML_PATH'])
    if not domain_status.prepareToWork(domainList, config):
        quit()
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