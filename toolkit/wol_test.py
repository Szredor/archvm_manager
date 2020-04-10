#!/usr/bin/env python3

import socket
import struct

def WakeOnLan(ethernet_address, broadcast, port):
    cmd = "lol"
    while cmd != 'y' and cmd != 'Y' and cmd != 'n' and cmd != 'N' and cmd != '':
        print("Do you want to send WakeOnLan to server?[Y/n] ", end="")
        cmd = input()
    if cmd == 'n' or cmd == 'N':
        return
     
    add_oct = []
    if len(ethernet_address) < 11:
        raise ValueError("MAC address is in wrong format. Check config file.")

    # Construct 6 byte hardware address
    add_oct = ethernet_address.split(':')
    if len(add_oct) != 6:
        add_oct = ethernet_address.split('-')
    if len(add_oct) != 6:
        add_oct.clear()
        for i in range(0,6):
            add_oct.append(ethernet_address[2*i:2*(i+1)])
    if len(add_oct) != 6:
        raise ValueError("MAC address is in wrong format. Check config file.")

    hwa = struct.pack('!BBBBBB', int(add_oct[0],16),
        int(add_oct[1],16),
        int(add_oct[2],16),
        int(add_oct[3],16),
        int(add_oct[4],16),
        int(add_oct[5],16))

    # Build magic packet
    msg = b'\xff' * 6 + hwa * 16

    # Send packet to broadcast address using UDP port 9
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
    soc.sendto(msg,(broadcast, port))
    soc.close()

WakeOnLan("70:85:c2:b3:85:aa", "192.168.100.255", 9)
