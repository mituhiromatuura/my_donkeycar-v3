import smbus2
import struct

class PsocI2cPwm:

	def __init__(self, cfg, addr=0x08):

		self.i2c = smbus2.SMBus(1)
		self.addr = addr

		self.ch1center = cfg.STEERING_CENTER_PWM
		self.ch1max = cfg.STEERING_RIGHT_PWM
		self.ch1min = cfg.STEERING_LEFT_PWM
		self.ch2center = cfg.THROTTLE_STOPPED_PWM
		self.ch2max = cfg.THROTTLE_FORWARD_PWM
		self.ch2min = cfg.THROTTLE_REVERSE_PWM

	def update(self):
		pass

	def run_threaded(self, angle, throttle):
		pass

	def run(self, angle, throttle):
		p = struct.pack('H', int(angle * ((self.ch1max - self.ch1min) / 2) + self.ch1center))
		#print(angle, (angle * ((self.ch1max - self.ch1min) / 2) + self.ch1center), p)
		self.i2c.write_i2c_block_data(self.addr, 1, p)
		p = struct.pack('H', int(throttle * ((self.ch2max - self.ch2min) / 2) + self.ch2center))
		#print(throttle, (throttle * ((self.ch2max - self.ch2min) / 2) + self.ch2center), p)
		self.i2c.write_i2c_block_data(self.addr, 2, p)

	def shutdown(self):
		pass

if __name__ == "__main__":
	i2c = smbus2.SMBus(1)
	data = [0x11, 0x02]
	i2c.write_i2c_block_data(0x08, 1, data)
