import time
import smbus

class PsocAdc:

    def __init__(self, addr=0x4a, poll_delay=0.0166):
        self.i2c = smbus.SMBus(1)
        self.addr = addr
        self.poll_delay = poll_delay
        self.on = True
        self.ad0 = 0
        self.ad1 = 0
        self.ad2 = 0
        self.ad3 = 0
        self.ad4 = 0
        self.ad5 = 0
        self.ad6 = 0

    def update(self):
        while self.on:
            self.poll()
            time.sleep(self.poll_delay)

    def swap(self, word):
        return ((word << 8) & 0xFF00) + ((word >> 8) & 0x00FF)

    def read(self, ch):
        config = 0x8583 + (ch<<12)
        try:
            self.i2c.write_word_data(self.addr, 1, self.swap(config))
            result = self.i2c.read_word_data(self.addr, 0) & 0xFFFF
            return self.swap(result)
        except KeyboardInterrupt:
            self.on = False
            print("KeyboardInterrupt:PsocAdc")
            return 0
        except:
            print('failed to read PsocAdc!!')
            return 0

    def poll(self):
        self.ad0 = self.read(0) / 0x7fff
        self.ad1 = self.read(1) / 0x7fff
        self.ad2 = self.read(2) / 0x7fff
        self.ad3 = self.read(3) / 0x7fff
        self.ad4 = self.read(4) / 0x7fff
        self.ad5 = self.read(5) / 0x7fff
        self.ad6 = self.read(6) / 0x7fff

    def run_threaded(self):
        return self.ad0, self.ad1, self.ad2, self.ad3, self.ad4, self.ad5, self.ad6

    def run(self):
        if self.on:
            self.poll()
        return self.ad0, self.ad1, self.ad2, self.ad3, self.ad4, self.ad5, self.ad6

    def shutdown(self):
        self.on = False


if __name__ == "__main__":
    p = PsocAdc(0x4b)
    while True:
        print(p.run())
        time.sleep(0.1)
     