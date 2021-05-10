import smbus

class Fram:

    def __init__(self, addr=0x50):

        self.i2c = smbus.SMBus(1)
        self.addr = addr

    def write(self, adr, val):
        try:
            self.i2c.write_word_data(self.addr, adr*2, int(val*1000))
        except:
            print('failed to Fram write!!')

    def read(self, adr):
        try:
            val = self.i2c.read_word_data(self.addr, adr*2)
            if val >= 0x8000:
                val =  val | ~0xffff
            return val / 1000.0, True
        except:
            print('failed to Fram read!!')
            return 0, False


if __name__ == "__main__":
    fram = Fram()

    '''
    fram.write(0, -0.2)
    fram.write(1, -0.4)
    fram.write(2, -0.6)
    fram.write(3, -0.8)
    fram.write(4, -10)
    '''
    fram.write(0, 0.7)
    fram.write(1, 1.0)
    fram.write(2, 0.4)
    fram.write(3, 0.5)
    fram.write(4, -2)

    print(fram.read(0))
    print(fram.read(1))
    print(fram.read(2))
    print(fram.read(3))
    print(int(fram.read(4)))
