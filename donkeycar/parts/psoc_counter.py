import time
import os
import struct

class PsocCounter:

	def __init__(self, dev_rc):
		self.on = True
		self.dev_rc = dev_rc

		self.ch0 = 0
		self.ch1 = 0
		self.ch2 = 0
		self.ch3 = 0

	def update(self):
		while self.on:
			while not os.path.exists(self.dev_rc):
				#print(self.dev_rc, "is missing")
				time.sleep(2)

			self.uart = open(self.dev_rc,'rb')
			print(self.dev_rc, "open")
			while self.on:
				d = self.uart.read(8)
				self.ch0, self.ch1, self.ch2, self.ch3 = struct.unpack('HHHH', d)

	def run_threaded(self):
		rpm = 0
		if self.ch0 != 0:
			rpm = 60 * 1000000 // self.ch0
		return \
			float((self.ch1 - 1530)/430), \
			float((self.ch2 - 1530)/430) * -1, \
			rpm, \
			self.ch1, \
			self.ch2, \
			self.ch0

	def shutdown(self):
		self.on = False
