#!/usr/bin/env python3

import socket
import configparser
import threading
import time
import signal
import sys
sys.path.append("./common/")

import xml_parsing
import sockets
import client_messages

config_file = 'archvm_manager.conf'
HEARTBEAT_CYCLE = 60

class thread_data():
    def __init__(self, bufSize):
        self._domainName = ""
        self._serverAddress = ""
        self._serverPort = 0
        self.bufSize = bufSize

        self.mutex = threading.Lock()
        self.isUsing = False

    def startUsing(self, name, serverAddress, serverPort):
        self.mutex.acquire()
        self._domainName = name
        self._serverAddress = serverAddress
        self._serverPort = serverPort
        self.isUsing = True
        self.mutex.release()

    def stopUsing(self):
        self.mutex.acquire()
        self._domainName = ""
        self._serverAddress = ""
        self._serverPort = 0
        self.isUsing = False
        self.mutex.release()

    def getHeartbeatData(self):
        return (self._domainName, self._serverAddress, self._serverPort)

def heartbeatThread(heartbeatData):
    while True:
        time.sleep(HEARTBEAT_CYCLE)
        heartbeatData.mutex.acquire()
        if heartbeatData.isUsing:
            name, ip, port = heartbeatData.getHeartbeatData()
            client_messages.heartbeatMessage(name, ip, port, heartbeatData.bufSize)
        heartbeatData.mutex.release()

def clientPrint(domainList):
    if domainList is None:
        print("List of domains doesn't exist.")
        return

    if len(domainList) == 0:
        print("List of domains is empty.")
        return

    for i in range(0,len(domainList)):
        print(f'{i+1}.', end='')
        if domainList[i].isGaming:
            print ('== GAMING == ', end='')
        else:
            print ('=== WORK === ', end='')
        print(f' {domainList[i].name} ', end='')
        if domainList[i].status.isRunning:
            print ('!!!')
        else:
            print ('zzz...')

        print(f'  Desciption: {domainList[i].description}')
        print(f'  Address: {domainList[i].description}')

        if not domainList[i].status.occupied:
            print('  READY TO USE')
        else:
            print(f'  OCCUPIED: {domainList[i].status.owner}')

def useDomain(domainData, config, threadData):
    if client_messages.connectMessage(domainData.name, config["COMMUNICATION"]["SERVER_IP"], int(config["COMMUNICATION"]["PORT"]), int(config["COMMUNICATION"]["BUF_SIZE"])):
        threadData.startUsing(domainData.name, config["COMMUNICATION"]["SERVER_IP"], int(config["COMMUNICATION"]["PORT"]))
    else:
        return True

    if domainData.isGaming:
        client_messages.runMoonlight(domainData.address, config['APPLICATIONS']['NVIDIA_CLIENT_PATH'])
    else:
        client_messages.runRDP(domainData.address, config['APPLICATIONS']['RDP_CLIENT_PATH'])

    client_messages.disconnectMessage(domainData.name, config["COMMUNICATION"]["SERVER_IP"], int(config["COMMUNICATION"]["PORT"]), int(config["COMMUNICATION"]["BUF_SIZE"]))
    threadData.stopUsing()

    return True
    
def main():
    working = True
    config = configparser.ConfigParser()
    config.read(config_file)

    #sockets.WakeOnLan(config["WAKEONLAN"]["SERVER_MAC"], config["WAKEONLAN"]["BROADCAST_ADDRESS"], int(config["WAKEONLAN"]["WOL_PORT"]))
    #start heartbeat daemon
    heartbeatData = thread_data(int(config["COMMUNICATION"]["BUF_SIZE"]))
    th = threading.Thread(target=heartbeatThread, args=(heartbeatData, ), daemon=True)
    th.start()

    domainList = client_messages.refreshMessage(config["COMMUNICATION"]["SERVER_IP"], int(config["COMMUNICATION"]["PORT"]), int(config["COMMUNICATION"]["BUF_SIZE"]))
    if domainList == None:
                sockets.WakeOnLan(config["WAKEONLAN"]["SERVER_MAC"], config["WAKEONLAN"]["BROADCAST_ADDRESS"], int(config["WAKEONLAN"]["WOL_PORT"]))
    clientPrint(domainList)
    client_messages.printHelp()

    while working:
        print(">", end="")
        cmd = input()

        #help command
        if cmd.startswith("help") or cmd.startswith("?"):
            client_messages.printHelp()
        elif cmd.startswith("exit"):
            working = False
        elif cmd[0] == 'r' and len(cmd) == 1:
            domainList = client_messages.refreshMessage(config["COMMUNICATION"]["SERVER_IP"], int(config["COMMUNICATION"]["PORT"]), int(config["COMMUNICATION"]["BUF_SIZE"]))
            if domainList == None:
                sockets.WakeOnLan(config["WAKEONLAN"]["SERVER_MAC"], config["WAKEONLAN"]["BROADCAST_ADDRESS"], int(config["WAKEONLAN"]["WOL_PORT"]))
            clientPrint(domainList)
        elif cmd[0].isnumeric():
            i = 1
            while len(cmd) > i and cmd[i].isnumeric():
                i+=1
            num = int(cmd[0:i])

            if num > 0 and num <= len(domainList):
                if not useDomain(domainList[num-1], config, heartbeatData):
                    working = False
            else:
                print("Wrong number of domain")
        else:
            print("Wrong command. Type \"help\" or \"?\" to show commands.")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Please use exit command next time")
    except SystemExit as err:
        pass