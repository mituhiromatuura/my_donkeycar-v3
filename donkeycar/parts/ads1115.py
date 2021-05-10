import time
import smbus

class Ads1115:

    def __init__(self, addr=0x4a, poll_delay=0.0166):
        self.i2c = smbus.SMBus(1)
        self.addr = addr
        self.poll_delay = poll_delay
        self.on = True
        self.volt0 = 0
        self.volt1 = 0
        self.volt2 = 0
        self.volt3 = 0

    def update(self):
        while self.on:
            self.poll()
            time.sleep(self.poll_delay)

    def swap(self, word):
        return ((word << 8) & 0xFF00) + ((word >> 8) & 0x00FF)

    def read(self, ch):
        config = 0xc583 + (ch<<12)
        try:
            self.i2c.write_word_data(self.addr, 1, self.swap(config))
            time.sleep(0.005)
            result = self.i2c.read_word_data(self.addr, 0) & 0xFFFF
            return self.swap(result)
        except:
            print('failed to read Ads1115!!')
            return 0

    def poll(self):
        self.volt0 = self.read(0) / 0x7fff
        self.volt1 = self.read(1) / 0x7fff
        self.volt2 = self.read(2) / 0x7fff
        self.volt3 = self.read(3) / 0x7fff

    def run_threaded(self):
        return self.volt0, self.volt1, self.volt2, self.volt3

    def run(self):
        self.poll()
        return self.volt0, self.volt1, self.volt2, self.volt3

    def shutdown(self):
        self.on = False


if __name__ == "__main__":
    p = Ads1115(0x4b)
    while True:
        print(p.run())
        time.sleep(0.1)
     