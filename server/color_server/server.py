#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 16 17:04:13 2016

@author: thibaud
"""

import logging
import os
from color_server.translator import Decoder
from color_server.gamma import Gamma
from color_server.tcp_receiver import TCPserver
from color_server.spi_writer import SPIwriter
from color_server.sync import UDPsync
from color_server.text import Text
import queue
import socket


class ColorServer():
    def __init__(self, port, sync_port, SPIspeed):
        gamma_coefs = [[1.12, 1.12, 1.12]]
        self.port = port
        self.sync_port = sync_port
        self.frame_length = len(gamma_coefs) * 324 * 3  # Length of receiving frames
        # New gamma matrix
        self.gamma_matrix = Gamma.gamma_matrix(gamma_coefs)

        self.receive_queue = queue.Queue()  # Receive FIFO
        self.emit_ring_buffer = [bytearray([0, 0, 0, 0])] * 28; # Emit ring buffer (26 regular frames + version frame + number frame)
        self.sync_queue = queue.Queue()  # Top synchro FIFO

        # Fill the two text frames (slab number, version, sub version)
        with open('.version', 'r') as version_file:
            version_string = version_file.read()
            version, sversion = version_string.split(".", 1)
            version = int(version)
            sversion = int(sversion)
        with open('.slab', 'r') as slab_file:
            slab = int(slab_file.read())
        self.text = Text(slab, version, sversion)
        self.emit_ring_buffer[26] = self.text.get_version_frame()
        self.emit_ring_buffer[27] = self.text.get_slab_number_frame()
        self.sync_queue.put(27) # Show slab number on start

        self.shutdown = False
        self.sync = None
        self.SPIspeed = SPIspeed

        self.sync_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP socket
        self.sync_sock.settimeout(3)
        self.sync_sock.bind(("", self.sync_port))                                        # Listen on port from everywhere

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # No port hold
        logging.info("Lancement du Thread d'écoute TCP...")
        self.sock.settimeout(3)
        # Start connection
        self.sock.bind(("", self.port))                                        # Listen on port 9999 from everywhere
        self.sock.listen(1)                                                    # 1 client max
        self.__connexion()


    # Server listening for LED data
    def start_server(self):
        logging.info("Lancement du ColorServer...")

        # New TCP server
        self.tcp_server = TCPserver(self.port, self.frame_length, self.receive_queue, self.sock, self.s, self.f)
        # New SPI writer
        self.spi_writer = SPIwriter(self.SPIspeed, self.emit_ring_buffer, self.sync_queue)
        # Create a translator (decode / encode)
        self.translator = Decoder(self.gamma_matrix, self.receive_queue, self.emit_ring_buffer)
        # Create the top synchro receiver
        self.sync = UDPsync(self.sync_port, self.sync_queue, self, self.sync_sock)

        self.shutdown = False

        self.tcp_server.start()
        self.spi_writer.start()
        self.translator.start()
        self.sync.start()

    def join_server(self):
        logging.info("Attente de la fin des threads")
        self.tcp_server.join()
        self.translator.join()
        self.spi_writer.join()
        try:
            self.sync.join()
        except RuntimeError:  # Bloquant comme attend la fin de join_serveur pour être join
            pass

    def stop_server(self):
        logging.info("Arrêt du serveur")
        self.shutdown = True
        self.tcp_server.stop()
        self.translator.stop()
        self.spi_writer.stop()
        self.sync.stop()

    def restart_server(self):
        logging.info("Redémarrage du serveur")
        os.system('/home/ledwall/ledwallslab/restart.sh')

    def __connexion(self):
        """
        Function called to start listening
        :return:
        """
        logging.info(str(self.sock))
        logging.info("En attente de connexion TCP")
        # Wait for connection
        self.s, self.f = self.sock.accept()
        logging.info("Client TCP connecté")
        self.buffer = b''  # Buffer reset

    @staticmethod
    def reboot():
        os.system('reboot')

    @staticmethod
    def poweroff():
        os.system('echo "ledwall"|sudo -S shutdown now')


