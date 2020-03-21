#! /usr/bin/env python3
import socket

import xml_parsing
import configparser
import sockets

#configFile = '/etc/archvm_manager'
configFile = 'test.conf'

def main():
    config = configparser.Config(configFile)
    #domain_list = xml_parsing.import_xml(config['CONSTANTS']['VMS_XML_PATH'])
    
    updateDomainsStatus(domainsList)

    sockets.handleCommands()

    print("server down")



if __name__ == '__main__':
    main()