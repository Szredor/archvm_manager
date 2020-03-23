#! /usr/bin/env python3

import xml.etree.ElementTree as ET



class Status():
    def __init__(self, occupied, owner, isRunning):
        self.occupied = occupied
        self.owner = owner
        self.isRunning = isRunning
        self.heartbeatCounter = 0
    def __repr__(self):
        return f'occupied: {self.occupied}, owner: {self.owner}, is running: {self.isRunning}, heartbeatCounter: {self.heartbeatCounter}'

    def printUser():
        raise NotImplementedError()

    def copyStatus(self, other):
        other.occupied = self.occupied
        other.owner = self.owner
        other.isRunning = self.isRunning
        other.heartbeatCounter = self.heartbeatCounter



# prototyp klasy domena
class Domain():
    def __init__(self, isGaming, name, description, address, status):
        self.isGaming = isGaming
        self.name = name
        self.description = description
        self.address = address
        self.status = status

    def __repr__(self):
        return f'is gaming: {str(self.isGaming)}\n name: {self.name}\n description: {self.description}\n address: {self.address}\n status: \n{self.status}'

    def printUser(self):
        raise NotImplementedError()


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
def printdomainList(domainList):
    for domain in domainList:
        print(domain)


#Tworzy string z xmlem do wyslania z listy domen bez czytania z pliku
def createXmlMessage(domainList): # zalazek
    testDomain = Domain(True, 'test', 'test', '111', Status(True, 'test', True))
    messageString = '<?xml version="1.0" encoding="UTF-8"?>'
    return messageString
    


if __name__ == '__main__':
    # testy funkcji 
    testdomainList = importDomains('docs/vms.xml')
    printdomainList(testdomainList)
    #createXmlMessage(testdomainList)

    ones = Status(0, 'siema', 1)
    twos = Status(0, 'drugi', 0)
    twos.heartbeatCounter = 2

    print(ones)
    print(twos)

    ones.copyStatus(twos)

    print(ones)
    print(twos)

    print("press any key to continue...")
    input()
