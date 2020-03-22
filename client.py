#!/usr/bin/env python3

import xml.etree.ElementTree as ET



# prototyp klasy domena
class Domain():
    def __init__(self, isGaming, name, description, address, status):
        self.isGaming = isGaming
        self.name = name
        self.description = description
        self.address = address
        self.status = status
    def __repr__(self):
        return f'is gaming: {str(self.isGaming)}\n name: {self.name}\n description: {self.description}\n address: {self.address}\n status: {self.status}\n'



# prototypowe definicje funkcji
def updateDomains(filename):
    domains = ET.parse(filename).getroot().getchildren()
    updatedDomains = []
    for domain in domains:
        if domain.tag == 'gaming':
            isGaming = True
        else:
            isGaming = False
        name = domain[0].text
        description = domain[1].text
        address = domain[2].text
        status = domain[3].attrib
        updatedDomains.append(Domain(isGaming, name, description, address, status))
    return updatedDomains


def printDomainList(domainList):
    for domain in domainList:
        print(domain)


def createXmlMessage(domainList, filename): # zalazek
    messageFile = open(filename, 'x')



# testy funkcji 
testdomainList = (updateDomains('vms.xml'))
printDomainList(testdomainList)
createXmlMessage(testdomainList, 'test.xml')