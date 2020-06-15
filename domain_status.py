#! /usr/bin/env python3

import threading
import time
import socket
import libvirt
import sys
sys.path.append("./common")

import xml_parsing
import sockets

HEARTBEATS_LOSS = 3
HEARTBEAT_CYCLE = 60

class HypervisorConnect():
    def __init__(self, hypervisorURI):
        self.__conn = self.__conn_hypervisor(hypervisorURI)
        if self.__conn is None:
            self.__criticalError = True
        else:
            self.__criticalError = False

    def __conn_hypervisor(self, driver):
    #connects with driver
        try:
            conn = libvirt.open(driver)
            #conn = libvirt.open("test:///default")
            return conn
        except libvirt.libvirtError as e:
            print("Cannot connect to hypervisor", driver)
            return None

    def check_running(self, name):
        '''checks if gave domain is not down'''
        try:
            dom = self.__conn.lookupByName(name)
            ID = dom.ID()
            if ID == -1: 
                return False
            return True
        except libvirt.libvirtError as e:
            print(e)
            return False

    def start_domain(self, name):
        try:
            dom = self.__conn.lookupByName(name)
            if dom.ID() == -1: 
                dom.create()
                return True
            return False
        except libvirt.libvirtError as e:
            print(e)
            return False

    def shutdown_domain(self, name):
        try:
            dom = self.__conn.lookupByName(name)
            if dom.ID() > -1: 
                dom.shutdown()
                return True
            return False
        except libvirt.libvirtError as e:
            print(e)
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
#Returns True on success, False otherwise. 
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

#closes connection with chosen hypervisor
def closeHypervisor() -> None:
    global hyper

    hyper.disconnect()
    pass

#Get status of domain. It's a reference to proper status of domain inside this software.
#It can be falsified when uses without caution.
#Returns Domain type on success, None otherwise.
def getDomain(domainList, name) -> xml_parsing.Domain:
    for dom in domainList:
        if dom.name == name:
            return dom
    return None

#Marks domain as using by owner (owner's address)
#Returns True on success, False otherwise.
def markUsing(dom, owner) -> bool:
    if dom.status.occupied and dom.status.owner == owner:
        return True

    if not dom.status.occupied:
        dom.status.owner = owner
        dom.status.occupied = True
        dom.status.heartbeatCounter = 0
        return True
    return False

#Marks domain as using by owner (owner's address)
#Returns True on success, False otherwise.
def markNotUsing(dom) -> bool:
    if dom.status.occupied:
        dom.status.owner = ''
        dom.status.occupied = False
        return True
    return False
            

def updateDomainsStatus(domainList) -> None:
    global domainsLock

    domainsLock.acquire()
    for dom in domainList:
        dom.status.isRunning = hyper.check_running(dom.name)
    domainsLock.release()

def handleHello(hello_path, sock):
    with open(hello_path) as f:
        content = f.readlines()

    result = ''.join(content)[:-1]

    try:
        sockets.writeSocket(sock, (chr(sockets.HELLO) + result).encode(encoding='utf-8'))
    except socket.timeout as err:
        pass


#Checks conditions and mark as occupied if all are right
#Returns str if error occured with error message. It is intented sending it to client.
#Return None otherwise.
def connectHandle(data, domainList, sock, owner) -> str:
    name = data.decode(encoding='utf-8')

    domainsLock.acquire()
    dom = getDomain(domainList, name)
    if dom is None:
        domainsLock.release()
        return f'Domain {name} does not exist'

    if not dom.status.isRunning:
        domainsLock.release()
        return f'Domain {name} does not work'

    if not markUsing(dom, owner):
        domainsLock.release()
        return f'Domain {name} is already occupied'

    try:
        sockets.writeSocket(sock, (chr(sockets.CONNECT) + 'OK').encode(encoding='utf-8'))
    except socket.timeout as err:
        markNotUsing(dom)
    domainsLock.release()
    return None
    
#Checks conditions and mark as not occupied if all are right
#Returns str if error occured with error message. It is intented sending it to client.
#Return None otherwise.
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
        return f'Domain {name} is not occupied'
    domainsLock.release()

    try:
        sockets.writeSocket(sock, (chr(sockets.DISCONNECT) + 'OK').encode(encoding='utf-8'))
    except socket.timeout as err:
        pass
    return None

#Zeros a heartbeatCounter for domains. It is used to check if client is still on the other side. 
#Returns str if error occured with error message. It is intented sending it to client.
#Return None otherwise.
def heartbeatHandle(data, domainList, sock, owner) -> str:
    name = data.decode(encoding='utf-8')

    domainsLock.acquire()
    dom = getDomain(domainList, name)
    if dom is None:
        domainsLock.release()
        return f'Heartbeat - Domain {name} does not exist'

    if not dom.status.isRunning:
        domainsLock.release()
        return f'Heartbeat - Domain {name} does not work'

    if not dom.status.occupied:
        domainsLock.release()
        return f'Heartbeat - Domain {name} is not occupied'

    if not dom.status.owner == owner:
        domainsLock.release()
        return f'Heartbeat - Domain {name} is not your property'

    dom.status.heartbeatCounter = 0
    domainsLock.release()

    try:
        sockets.writeSocket(sock, (chr(sockets.HEARTBEAT) + 'OK').encode(encoding='utf-8'))
    except socket.timeout as err:
        pass
    return None

def bootHandle(data, domainList, sock) -> str:
    name = data.decode(encoding='utf-8')

    domainsLock.acquire()
    dom = getDomain(domainList, name)
    if dom is None:
        domainsLock.release()
        return f'Domain {name} does not exist.'

    inside = dom.status.isRunning
    outside = hyper.check_running(name)
    domainsLock.release()

    if outside == True and inside == True:
         return f'Domain {name} is up, cannot boot.'

    if outside != inside:
        if outside:
            return f'Domain {name} is down in hypervisor. If you really want to boot it up, refresh and try again, please.'
        else:
            return f'Domain {name} is already running but status has wrong information. Please refresh.'

    if not hyper.start_domain(name):
        return f'Domain {name} cannot be started.'

    try:
        sockets.writeSocket(sock, (chr(sockets.BOOT) + 'OK').encode(encoding='utf-8'))
    except socket.timeout as err:
        hyper.shutdown_domain(name)

def shutdownHandle(data, domainList, sock) -> str:
    name = data.decode(encoding='utf-8')

    domainsLock.acquire()
    dom = getDomain(domainList, name)
    if dom is None:
        domainsLock.release()
        return f'Domain {name} does not exist.'

    inside = dom.status.isRunning
    outside = hyper.check_running(name)
    domainsLock.release()

    if outside == False and inside == False:
        return f'Domain {name} is down, cannot shutdown.'
    
    if outside != inside:
        if outside:
            return f'Domain {name} is running in hypervisor. If you really want to shut it down, refresh and try again, please.'
        else:
            return f'Domain {name} is down in hypervisor. Please refresh.'

    if not hyper.shutdown_domain(name):
        return f'Domain {name} cannot be shuted down.'

    try:
        sockets.writeSocket(sock, (chr(sockets.SHUTDOWN) + 'OK').encode(encoding='utf-8'))
    except socket.timeout as err:
        hyper.start_domain(name)

#Reloads data about virtual machines configured in XML file.
#Copies status of every still exeisting domains.
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
