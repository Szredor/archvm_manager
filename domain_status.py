#! /usr/bin/env python3

import threading
import time
import xml_parsing
import libvirt

HEARTBEATS_LOSS = 3

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
    time.sleep(60)

    #critical section to increment heartbetConters in domainsStatus list
    domainsLock.acquire()
    for dom in domainsStatus:
        if dom.status:
            dom.heartbeatCounter = dom.heartbeatCounter + 1
            if dom.status.heartbeatCountser > HEARTBEATS_LOSS:
                #dom.owner
                pass

    domainsLock.release()

#Intilizes connection with hypervisor, create heartbeat thread and creates lock
def prepareToWork(domainsStatus) -> bool:
    global hyper
    global domainsLock

    hyper = HypervisorConnect('qemu:///system')
    if hyper.isCriticalError:
        return False

    domainsLock = threading.Lock()

    threading.Thread(target=heartbeatIncrementWorker, args=(domainsStatus, domainsLock), daemon=True)
    return True


def closeHypervisor() -> None:
    global hyper

    hyper.disconnect()

def isInUse(domainsList, name):
    for dom in domainsList:
        if dom.name == name:
            return dom.status
    raise LookupError("Domain not found")

def domainExists(domainsList, name):
    for dom in domainsList:
        if dom.name == name:
            return True
    return False

def markUsing(domainList, name, owner):
    for dom in domainsList:
        if dom.name == name:
            if not dom.status.occupied:
                dom.status.owner = owner
                dom.status.occupied = True
                return true
            else:
                return False
    return False
            

def updateDomainsStatus(domainsList) -> None:
    for dom in domainsList:
        dom.status.isRunning = hyper.check_running(dom.name)

#to do
def connectHandle(data, domainsList, sock, owner) -> str:
    name = data.decode(encoding='utf-8')
    
#to do
def disconnectHandle(data, domainsList, sock, owner) -> str:
    pass
#to do
def heartbeatHandle(data, domainsList, sock, owner) -> str:
    pass

#test it!!!
def changeToNewDomains(domainsList, newList):
    global domainsLock

    domainsLock.acquire()

    for tDom in newList:
        for d in domainsList:
            if d.name == tDom.name:
                d.status.copyStatus(tDom.status)
    
    domainsList.clear()
    for tDom in newList:
        domainsList.append(tDom)

    domainsLock.release()
