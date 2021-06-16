import time
import smbus

class Ina226:

    def __init__(self, addr=0x48, poll_delay=0.0166):
        self.i2c = smbus.SMBus(1)
        self.addr = addr
        self.poll_delay = poll_delay
        self.on = True

    def update(self):
        while self.on:
            self.poll()
            time.sleep(self.poll_delay)

    def poll(self):
        try:
            word = self.i2c.read_word_data(self.addr, 0x02) & 0xFFFF
            result = ((word << 8) & 0xFF00) + ((word >> 8) & 0x00FF)
            self.volt = result * 1.25 / 1000
        except KeyboardInterrupt:
            self.on = False
            print("KeyboardInterrupt:Ina226")
        except:
            print('failed to read Ina226!!')

    def run_threaded(self):
        return self.volt

    def run(self):
        if self.on:
            self.poll()
        return self.volt

    def shutdown(self):
        self.on = False


if __name__ == "__main__":
    iter = 0
    p = Ina226()
    #p = Ina226(addr=0x49)
    while iter < 100:
        data = p.run()
        print(data)
        time.sleep(0.1)
        iter += 1
     