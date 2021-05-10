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

        GPIO.setmode(GPIO.BOARD)
        self.pi = pigpio.pi()
        self.gpio_pin_fpga_reset = 12
        GPIO.setup(self.gpio_pin_fpga_reset, GPIO.OUT)
        GPIO.output(self.gpio_pin_fpga_reset, GPIO.LOW)

    def poll(self, esc_on):
        if not esc_on:
            GPIO.output(self.gpio_pin_fpga_reset, GPIO.LOW)
            self.reset_time = 1000/33 #FPGAƒŠƒZƒbƒg‰ðœ’x‰„ŽžŠÔ

        elif self.reset_time > 0:
            self.reset_time = self.reset_time - 1

        else:
            GPIO.output(self.gpio_pin_fpga_reset, GPIO.HIGH)

            s, d = self.pi.spi_read(self.h, 8)
            self.ch1, self.ch2, self.ch3, self.ch4 = struct.unpack('HHHH', d)

    def run_threaded(self):
        return self.ch1, self.ch2, self.ch3, self.ch4

    def run(self, esc_on):
        self.poll(esc_on)
        return self.ch1, self.ch2, self.ch3, self.ch4

    def shutdown(self):
        self.on = False
