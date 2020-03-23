#! /usr/bin/env python3

import xml.etree.ElementTree as ET



class Status():
    def __init__(self, occupied, owner, isRunning):
        self.occupied = occupied
        self.owner = owner
        self.isRunning = isRunning
    def __repr__(self):
        return f'occupied: {self.occupied}, owner: {self.owner}, is running: {self.isRunning}'
    def printUser():
        pass
    def copyStatus(self, other):
        for member in self:
            other.member = self.member



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
    def printUser(self):
        pass


#wczytuje poczatkowy stan domen z pliku
def importDomains(filename):
    importedDomains = []
    domains = ET.parse(filename).getroot()
    for domain in domains:
        domainInitList = []
        domainInitList.append(bool(domain.tag == 'gaming'))
        for child in domain:
            if child.tag  != 'status':
                domainInitList.append(child.text)
            else:
                status = Status(bool(child.attrib.get('occupied') == '1'), child[0].text, bool(child[1].text == '1'))
                domainInitList.append(status)         
        importedDomains.append(Domain(*domainInitList))

    return importedDomains


#wypisuje domeny na ekranie 
def printDomainsList(domainList):
    for domain in domainList:
        print(domain)


#Tworzy string z xmlem do wyslania z listy domen bez czytania z pliku
def createXmlMessage(domainsList): # zalazek
    testDomain = Domain(True, 'test', 'test', '111', Status(True, 'test', True))
    messageString = '<?xml version="1.0" encoding="UTF-8"?>'
    return messageString
    


if __name__ == '__main__':
    # testy funkcji 
    testdomainList = importDomains('vms.xml')
    printDomainsList(testdomainList)
    #createXmlMessage(testdomainList)
    print("press any key to continue...")
    input()
