#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 16 17:22:21 2016

@author: thibaud
"""

import socket

# Create a UDP Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.sendto((1).to_bytes(1, byteorder='big'), ("127.0.0.1", 8888))
# sock.sendto("l".encode(), ("127.0.0.1", 8888))

