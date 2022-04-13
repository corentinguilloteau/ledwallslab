#!/usr/bin/python3
# -*- coding: utf-8 -*-

from configparser import Interpolation
import logging
from queue import Empty
from threading import Thread
import time
import tkinter as tk
from PIL import Image, ImageTk
import PIL
import numpy as np
import cv2

HEIGHT = 18
WIDTH = 18

class GUIWriter(Thread):
    def __init__(self, emit_ring_buffer, sync_queue):
        Thread.__init__(self)

        # Create the window
        self.window = tk.Tk()
        self.window.resizable(width = True, height = True)

        # Saving queue pointer
        self.emit_ring_buffer = emit_ring_buffer
        self.sync_queue = sync_queue

        # Stop flag
        self.terminated = False

    # Server listening for LED data
    def run(self):
        logging.info("Thread de communication SPI opérationnel")
        # The thread write available data on the SPI bus
        while not self.terminated:
            try:
                frame_to_show = self.sync_queue.get(timeout = 3)   # wait until frame number to show UDP received
            except Empty:
                continue

            buffer = self.emit_ring_buffer[frame_to_show]
            
            pixels = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

            print(len(buffer))

            if len(buffer) >= WIDTH*HEIGHT*4:

                for h in range(0, HEIGHT):
                    if h%2 == 0:

                        for w in range(0, WIDTH):
                            pixels[h][w][0] = buffer[h*WIDTH*4+w*4+1+4]
                            pixels[h][w][1] = buffer[h*WIDTH*4+w*4+2+4]
                            pixels[h][w][2] = buffer[h*WIDTH*4+w*4+3+4]
                    else:
                        for w in range(0, WIDTH):
                            pixels[h][WIDTH-w-1][0] = buffer[h*WIDTH*4+w*4+1+4]
                            pixels[h][WIDTH-w-1][1] = buffer[h*WIDTH*4+w*4+2+4]
                            pixels[h][WIDTH-w-1][2] = buffer[h*WIDTH*4+w*4+3+4]

                # img = Image.fromarray(pixels)
                # img.save('.temp.bmp')

                pixels = cv2.resize(pixels, (360, 360), interpolation= cv2.INTER_NEAREST) 

                cv2.imshow('test', pixels)
                cv2.waitKey(1)

    def stop(self):
        self.terminated = True