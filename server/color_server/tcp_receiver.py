#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 16 17:04:13 2016

@author: thibaud
"""

import logging
import socket
from threading import Thread


class TCPserver(Thread):
    def __init__(self, port, frame_length, queue, sock, accept_sock, other_sock):
        """
        This constructor init TCP socket
        :param port: default 9999
        :param frame_length: default 1 slab * 324 LEDs * 3 colors = 972 bytes long
        :param queue: queue to put data in
        """
        Thread.__init__(self)

        self.sock = sock

        self.queue = queue
        self.frame_length = frame_length + 1 # +1 byte for frame number between 0 and 25 (used for synchro) at the beginging
        self.s = accept_sock
        self.f = other_sock
        self.buffer = b'' # Buffer's type is bytes
        self.terminated = False

    def run(self):
        """
        Thread function
        :return:
        """
        
        while not self.terminated:
            while len(self.buffer) < self.frame_length and not self.terminated:
                try:
                    b = self.s.recv(1024) # Should be a power of 2. Must be under 1944 (two frames). Try 512 ?
                except socket.error:
                    continue
                except socket.timeout:
                    continue
                # In case of disconnection
                if len(b) == 0:
                    logging.info("Le client s'est déconnecté")
                    self.s.close()
                    self.s = None
                else:
                    self.buffer += b

            # Write in the reception FIFO only 1 frame
            self.queue.put(self.buffer[:self.frame_length])
            self.buffer = self.buffer[self.frame_length:]

    def reset_connection(self):
        """
        Function called to reset TCP socket
        :return:
        """
        if self.s is None:
            return
        logging.info("Réinitialisation de la connexion TCP")
        self.s.close()
        self.s = None

    def stop(self):
        self.terminated = True

