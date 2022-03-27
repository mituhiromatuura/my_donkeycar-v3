import smbus2
import struct

class PsocI2cPwm:

	def __init__(self, addr=0x08):

		self.i2c = smbus2.SMBus(1)
		self.addr = addr

	def update(self):
		pass

	def run_threaded(self, angle, throttle):
		pass

	def run(self, angle, throttle):
		p = struct.pack('H', angle)
		self.i2c.write_i2c_block_data(self.addr, 1, p)
		p = struct.pack('H', throttle)
		self.i2c.write_i2c_block_data(self.addr, 2, p)

	def shutdown(self):
		pass

if __name__ == "__main__":
	i2c = smbus2.SMBus(1)
	data = [0x11, 0x02]
	i2c.write_i2c_block_data(0x08, 1, data)
