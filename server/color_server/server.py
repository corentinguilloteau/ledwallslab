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
from color_server.gui_writer import GUIWriter
from color_server.sync import UDPsync
from color_server.text import Text
import queue


class ColorServer():
    def __init__(self, port, sync_port, SPIspeed):
        gamma_coefs = [[1.12, 1.12, 1.12]]
        self.port = port
        self.sync_port = sync_port
        self.frame_length = len(gamma_coefs) * 324 * 3  # Length of receiving frames
        # New gamma matrix
        self.gamma_matrix = Gamma.gamma_matrix(gamma_coefs)

        self.receive_queue = queue.Queue()  # Receive FIFO
        self.emit_ring_buffer = [bytearray([0, 0, 0, 0])] * 29; # Emit ring buffer (26 regular frames + version frame + number frame + shutdown frame)
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
        self.emit_ring_buffer[28] = self.text.display_shutdown()
        self.sync_queue.put(27) # Show slab number on start

        self.shutdown = 0
        self.SPIspeed = SPIspeed

    # Server listening for LED data
    def start_server(self):
        # New TCP server
        self.tcp_server = TCPserver(self.port, self.frame_length, self.receive_queue)
        # New SPI writer
        # TODO: plug ourself here
        self.spi_writer = GUIWriter(self.emit_ring_buffer, self.sync_queue)
        # Create a translator (decode / encode)
        self.translator = Decoder(self.gamma_matrix, self.receive_queue, self.emit_ring_buffer)
        # Create the top synchro receiver
        self.sync = UDPsync(self.sync_port, self.sync_queue, self)

        self.shutdown = 0

        logging.info("Lancement du ColorServer...")
        self.tcp_server.start()
        self.spi_writer.start()
        self.translator.start()
        self.sync.start()

    def join_server(self):
        logging.info("Attente de la fin des threads")
        self.tcp_server.join()
        self.translator.join()
        self.spi_writer.join()
       # try:
        self.sync.join()
        #except RuntimeError:  # Bloquant comme attend la fin de join_serveur pour être join
         #   pass

    def stop_server(self):
        logging.info("Arrêt du serveur")
        self.tcp_server.stop()
        self.translator.stop()
        self.spi_writer.stop()
        self.sync.stop()

    @staticmethod
    def reboot():
        os.system('echo "ledwall"|sudo -S reboot now')

    @staticmethod
    def poweroff():
        os.system('echo "ledwall"|sudo -S shutdown now')


