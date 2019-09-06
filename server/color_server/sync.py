#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 16 17:04:13 2016

@author: thibaud
"""

import os
import logging
import socket
from threading import Thread


class UDPsync(Thread):
    def __init__(self, port, sync_queue, server, sock):
        Thread.__init__(self)

        # Create socket
        self.sock = sock
        

        self.port = port
        self.sync_queue = sync_queue
        self.server = server
        self.is_live = True
        self.terminated = False
        print("MY PID IS: {}".format(os.getpid()))

    # Server listening for sync top
    def run(self):
        logging.info("Lancement du Thread d'écoute de synchronisation...")
        # Start connection
        last = 0
        while not self.terminated:
            try:
                frame_to_show, emitter = self.sock.recvfrom(1)
            except socket.timeout:
                continue
            
            frame_to_show = int.from_bytes(frame_to_show, byteorder='big')
            if 0 <= frame_to_show <= 25 and self.is_live:   # while frame_to_show comes from UDP transmission, errors are possible
                self.sync_queue.put(frame_to_show)
            elif frame_to_show == 118 and last == 118:  # 118 = 'v' --> show version
                logging.info("Affichage de la version")
                self.sync_queue.put(26)
                self.is_live = False
                
            elif frame_to_show == 110 and last == 110:  # 110 = 'n' --> show slab number
                logging.info("Affichage du numéro de la dalle")
                self.sync_queue.put(27)
                self.is_live = False
                
            elif frame_to_show == 115 and last == 115:  # 115 = 's' --> restart server
                logging.info("Redémarrage du serveur")
                self.server.restart_server()
            elif frame_to_show == 114 and last == 114:  # 114 = 'r' --> reboot slab
                logging.info("Reboot")
                self.server.reboot()
            elif frame_to_show == 108 and last == 108:  # 108 = 'l' --> return live
                logging.info("Retour au live")
                self.is_live = True
            elif frame_to_show == 112 and last == 112:  # 112 = 'p' --> shutdown the slab
                logging.info("Shutdown")
                self.server.stop_server()
            last = frame_to_show

    def stop(self):
        self.terminated= True
