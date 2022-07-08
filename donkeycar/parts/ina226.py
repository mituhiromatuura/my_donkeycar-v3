import time
import smbus

class Ina226:

    def __init__(self, addr):
        self.i2c = smbus.SMBus(1)
        self.addr = addr

    def run(self):
        word = self.i2c.read_word_data(self.addr, 0x02) & 0xFFFF
        result = ((word << 8) & 0xFF00) + ((word >> 8) & 0x00FF)
        return result * 1.25 / 1000
