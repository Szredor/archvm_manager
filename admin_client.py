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
        print(f'  Address: {domainList[i].address}')

        if not domainList[i].status.occupied:
            print('  READY TO USE')
        else:
            print(f'  OCCUPIED: {domainList[i].status.owner}')
    
def main():
    working = True
    config = configparser.ConfigParser()
    config.read(config_file)

    server_down = True
    while server_down:
        try:
            if not client_messages.helloMessage(config["COMMUNICATION"]["SERVER_IP"], int(config["COMMUNICATION"]["PORT"]), int(config["COMMUNICATION"]["BUF_SIZE"])):
                raise RuntimeError()

            domainList = client_messages.refreshMessage(config["COMMUNICATION"]["SERVER_IP"], int(config["COMMUNICATION"]["PORT"]), int(config["COMMUNICATION"]["BUF_SIZE"]))
            if domainList == None:
                raise RuntimeError()

            #Server responded correctly
            server_down = False
        except RuntimeError:
            sockets.WakeOnLan(config["WAKEONLAN"]["SERVER_MAC"], config["WAKEONLAN"]["BROADCAST_ADDRESS"], int(config["WAKEONLAN"]["WOL_PORT"]))
            print("Press enter to try again. If you want to quit type exit and enter.")
            cmd = input()
            if input.startswith("exit"):
                working = False
                server_down = False
    if not working:
        return 

    clientPrint(domainList)
    client_messages.printHelp()

    while working:
        print(">", end="")
        cmd = input()

        if len(cmd) < 1:
            continue

        #help command
        if cmd.startswith("help") or cmd.startswith("?"):
            client_messages.printAdminHelp()
        #exit command
        elif cmd.startswith("exit"):
            working = False
        #refresh command
        elif cmd[0] == 'r' and len(cmd) == 1:
            domainList = client_messages.refreshMessage(config["COMMUNICATION"]["SERVER_IP"], int(config["COMMUNICATION"]["PORT"]), int(config["COMMUNICATION"]["BUF_SIZE"]))
            if domainList == None:
                sockets.WakeOnLan(config["WAKEONLAN"]["SERVER_MAC"], config["WAKEONLAN"]["BROADCAST_ADDRESS"], int(config["WAKEONLAN"]["WOL_PORT"]))
            clientPrint(domainList)
        #change state of chosen machine
        elif cmd[0].isnumeric():
            i = 1
            while len(cmd) > i and cmd[i].isnumeric():
                i+=1
            num = int(cmd[0:i])

            if num > 0 and num <= len(domainList):
                if domainList[num-1].status.isRunning:
                    client_messages.shutdownMessage(domainList[num-1].name, config["COMMUNICATION"]["SERVER_IP"], int(config["COMMUNICATION"]["PORT"]), int(config["COMMUNICATION"]["BUF_SIZE"]))
                else:
                    client_messages.bootMessage(domainList[num-1].name, config["COMMUNICATION"]["SERVER_IP"], int(config["COMMUNICATION"]["PORT"]), int(config["COMMUNICATION"]["BUF_SIZE"]))
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
