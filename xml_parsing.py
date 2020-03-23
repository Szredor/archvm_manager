#! /usr/bin/env python3

import xml.etree.ElementTree as ET

# prototyp klasy domena
class Domain():
    def __init__(self, isGaming, name, description, address, status):
        self.isGaming = isGaming
        self.name = name
        self.description = description
        self.address = address
        self.status = status
        self.heartbeatCounter = 0
    def __repr__(self):
        return f'is gaming: {str(self.isGaming)}\n name: {self.name}\n description: {self.description}\n address: {self.address}\n status: {self.status}\n'

#wczytuje poczatkowy stan domen z pliku
def importDomains(filename):
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
        status = bool(domain[3].attrib['occupied'])
        updatedDomains.append(Domain(isGaming, name, description, address, status))
    return updatedDomains

#wypisuje domeny na ekranie 
def printDomainsList(domainList):
    for domain in domainList:
        print(domain)

#Tworzy string z xmlem do wyslania z listy domen bez czytania z pliku
def createXmlMessage(domainList): # zalazek
    pass


if __name__ == '__main__':
    # testy funkcji 
    testdomainList = importDomains('docs/vms.xml')
    printDomainsList(testdomainList)
    createXmlMessage(testdomainList)
    print("press any key to continue...")
    input()
