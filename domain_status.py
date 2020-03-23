#! /usr/bin/env python3

import threading
import time
import socket

import xml_parsing
import sockets
import libvirt

HEARTBEATS_LOSS = 3
HEARTBEAT_CYCLE = 60





class HypervisorConnect():

    def __init__(self, hypervisorURI):
        self.__conn = self.__conn_hypervisor(hypervisorURI)
        if self.__conn is None:
            self.__criticalError = True
        else:
            self.__criticalError = True

    def __conn_hypervisor(self, driver):
    #connects with driver
        try:
            #conn = libvirt.open(driver)
            conn = libvirt.open("test:///default")
            return conn
        except libvirt.libvirtError as e:
            print("Cannot connect to hypervisor", driver)
            return None

    def check_running(self, name):
        '''checks if gave domain is not down'''
        try:
            dom = self.__conn.lookupByName(name)
            ID = dom.ID()
            if ID == -1: return False
            return True
        except libvirt.libvirtError as e:
            return False

    def isCriticalError(self):
        return self.__criticalError

    def disconnect(self):
        try:
            self.__conn.close()
        except libvirt.libvirtError as e:
            print(e.get_error_message())
        print ("Hypervisor connection closed")

#Thread to increment and expropriate domain if neccesary
def heartbeatIncrementWorker(domainsStatus, domainsLock):
    while True:
        time.sleep(HEARTBEAT_CYCLE)
        
        #critical section to increment heartbetConters in domainsStatus list
        domainsLock.acquire()
        for dom in domainsStatus:
            if dom.status.occupied:
                dom.status.heartbeatCounter = dom.status.heartbeatCounter + 1
                if dom.status.heartbeatCounter > HEARTBEATS_LOSS:
                    markNotUsing(dom)

        domainsLock.release()

#Intilizes connection with hypervisor, create heartbeat thread and creates lock
def prepareToWork(domainsStatus, config) -> bool:
    global hyper
    global domainsLock

    hyper = HypervisorConnect(config['VIRTUALIZATION']['HYPERVISOR_URI'])
    if hyper.isCriticalError():
        return False

    domainsLock = threading.Lock()

    th = threading.Thread(target=heartbeatIncrementWorker, args=(domainsStatus, domainsLock), daemon=True)
    th.start()
    return True


def closeHypervisor() -> None:
    global hyper

    hyper.disconnect()
    pass

def getDomain(domainList, name) -> xml_parsing.Domain:
    for dom in domainList:
        if dom.name == name:
            return dom
    return None

def markUsing(dom, owner) -> bool:
    if not dom.status.occupied:
        dom.status.owner = owner
        dom.status.occupied = True
        dom.status.heartbeatCounter = 0
        return True
    return False

def markNotUsing(dom) -> bool:
    if dom.status.occupied:
        dom.status.owner = ''
        dom.status.occupied = False
        return True
    return False
            

def updateDomainsStatus(domainList) -> None:
    domainsLock.acquire()
    for dom in domainList:
        dom.status.isRunning = hyper.check_running(dom.name)
        pass
    domainsLock.release()


#checks considtions and mark as occupied if all are right
def connectHandle(data, domainList, sock, owner) -> str:
    name = data.decode(encoding='utf-8')

    domainsLock.acquire()
    dom = getDomain(domainList, name)
    if dom is None:
        domainsLock.release()
        return f'Domain {name} does not exist'

    dom.status.isRunning = True
    if not dom.status.isRunning:
        domainsLock.release()
        return f'Domain {name} does not work'

    if not markUsing(dom, owner):
        domainsLock.release()
        return f'Domain {name} is not occupied'

    try:
        sockets.writeSocket(sock, (chr(sockets.CONNECT) + 'OK').encode(encoding='utf-8'))
    except socket.timeout as err:
        markNotUsing(dom)
    domainsLock.release()
    
#to do
def disconnectHandle(data, domainList, sock, owner) -> str:
    name = data.decode(encoding='utf-8')

    domainsLock.acquire()
    dom = getDomain(domainList, name)
    if dom is None:
        domainsLock.release()
        return f'Domain {name} does not exist'

    if not dom.status.isRunning:
        domainsLock.release()
        return f'Domain {name} does not work'

    if not markNotUsing(dom):
        domainsLock.release()
        return f'Domain {name} is already occupied'
    domainsLock.release()

    try:
        sockets.writeSocket(sock, (chr(sockets.DISCONNECT) + 'OK').encode(encoding='utf-8'))
    except socket.timeout as err:
        pass
#to do
def heartbeatHandle(data, domainList, sock, owner) -> str:
    name = data.decode(encoding='utf-8')

    domainsLock.acquire()
    dom = getDomain(domainList, name)
    if dom is None:
        domainsLock.release()
        return f'Domain {name} does not exist'

    if not dom.status.isRunning:
        domainsLock.release()
        return f'Domain {name} does not work'

    if not dom.status.occupied:
        domainsLock.release()
        return f'Domain {name} is not occupied'

    if not dom.status.owner == owner:
        domainsLock.release()
        return f'Domain {name} is not your property'

    dom.status.heartbeatCounter = 0
    domainsLock.release()

    try:
        sockets.writeSocket(sock, (chr(sockets.HEARTBEAT) + 'OK').encode(encoding='utf-8'))
    except socket.timeout as err:
        pass


def changeToNewDomains(domainList, newList):
    global domainsLock

    domainsLock.acquire()

    for tDom in newList:
        for d in domainList:
            if d.name == tDom.name:
                d.status.copyStatus(tDom.status)
    
    domainList.clear()
    for tDom in newList:
        domainList.append(tDom)

    domainsLock.release()
