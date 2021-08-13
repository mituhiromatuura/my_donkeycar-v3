import smbus2
import struct

class Fram:

	def __init__(self, addr=0x50):

		self.i2c = smbus2.SMBus(1)
		self.addr = addr

	def write_l(self, adr, val):
		p = struct.pack('l', val)
		try:
			self.i2c.write_i2c_block_data(self.addr, adr*16, p)
		except:
			print('failed to Fram write!!')

	def read_l(self, adr):
		try:
			a = self.i2c.read_i2c_block_data(self.addr, adr*16, 4)
			p = struct.pack('BBBB', a[0], a[1],  a[2],  a[3])
			data = struct.unpack('l', p)
			return data[0], True
		except:
			print('failed to Fram read!!')
			return 0, False

	def write_f(self, adr, val):
		p = struct.pack('f', val)
		try:
			self.i2c.write_i2c_block_data(self.addr, adr*16, p)
		except:
			print('failed to Fram write!!')

	def read_f(self, adr):
		try:
			a = self.i2c.read_i2c_block_data(self.addr, adr*16, 4)
			p = struct.pack('BBBB', a[0], a[1],  a[2],  a[3])
			data = struct.unpack('f', p)
			return data[0], True
		except:
			print('failed to Fram read!!')
			return 0, False


if __name__ == "__main__":
	fram = Fram()

	fram.write_f(0, 1.0)
	print(fram.read_f(0))
	fram.write_f(1, 1.0)
	print(fram.read_f(1))
