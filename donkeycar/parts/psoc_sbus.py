import time
import os
import struct

class PsocCounter:

	def __init__(self, cfg, dev_rc):
		self.on = True
		self.cfg = cfg
		self.dev_rc = dev_rc

		self.ch1center = self.cfg.SBUS_CH1_CENTER
		self.ch1max = self.cfg.SBUS_CH1_MAX
		self.ch1min = self.cfg.SBUS_CH1_MIN
		self.ch2center = self.cfg.SBUS_CH2_CENTER
		self.ch2max = self.cfg.SBUS_CH2_MAX
		self.ch2min = self.cfg.SBUS_CH2_MIN

		self.ch0 = 0
		self.ch1 = 0
		self.ch2 = 0
		self.ch3 = 0
		self.ch4 = 0
		self.ch5 = 0
		self.ch6 = 0
		self.ch7 = 0

	def update(self):
		while self.on:
			while not os.path.exists(self.dev_rc):
				#print(self.dev_rc, "is missing")
				time.sleep(2)

			self.uart = open(self.dev_rc,'rb')
			print(self.dev_rc, "open")
			while self.on:
				d = self.uart.read(16)
				self.ch0, self.ch1, self.ch2, self.ch3, self.ch4, self.ch5, self.ch6, self.ch7 = struct.unpack('HHHHHHHH', d)

	def run_threaded(self):
		rpm = 0
		if self.ch0 != 0:
			rpm = 60 * 1000000 // self.ch0
		return \
			float((self.ch1 - self.ch1center)/((self.ch1max - self.ch1min) / 2)), \
			float((self.ch2 - self.ch2center)/((self.ch2max - self.ch2min) / 2)), \
			rpm, \
			self.ch1, \
			self.ch2, \
			self.ch0

	def shutdown(self):
		self.on = False
