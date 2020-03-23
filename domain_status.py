#! /usr/bin/env python3

import threading
import time
import xml_parsing

HEARTBEATS_LOSS = 3

#Thread to increment and expropriate domain if neccesary
def heartbeatIncrementWorker(domainsStatus, domainsLock):
    time.sleep(60)

    #critical section to increment heartbetConters in domainsStatus list
    domainsLock.acquire()
    for dom in domainsStatus:
        if dom.status:
            dom.heartbeatCounter = dom.heartbeatCounter + 1
            if dom.heartbeatCountser > HEARTBEATS_LOSS:
                #dom.owner
                pass

    domainsLock.release()

def connectHandle(data, domainsList):
    pass

def disconnectHandle(data, domainsList):
    pass

def heartbeatHandle(data, domainsList):
    pass