import RPi.GPIO as GPIO
import pigpio
import struct

class Spi:

    def __init__(self):
        self.on = True

        self.ch1 = 0
        self.ch2 = 0
        self.ch3 = 0
        self.ch4 = 0

        self.reset_time = 0

        self.pi = pigpio.pi()
        self.h = self.pi.spi_open(0, 66000, 1)

    def poll(self, esc_on):
        s, d = self.pi.spi_read(self.h, 8)
        self.ch1, self.ch2, self.ch3, self.ch4 = struct.unpack('HHHH', d)

    def run_threaded(self):
        return self.ch1, self.ch2, self.ch3, self.ch4

    def run(self, esc_on):
        self.poll(esc_on)
        return self.ch1, self.ch2, self.ch3, self.ch4

    def shutdown(self):
        self.on = False
