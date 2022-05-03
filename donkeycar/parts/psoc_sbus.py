import time
import os
import struct
import queue

class PsocCounter:

	def __init__(self, cfg, dev_rc, q_button):
		self.on = True
		self.cfg = cfg
		self.dev_rc = dev_rc
		self.q_button = q_button

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
		self.ch8 = 0

	def update(self):
		while self.on:
			while not os.path.exists(self.dev_rc):
				#print(self.dev_rc, "is missing")
				time.sleep(2)

			self.uart = open(self.dev_rc,'rb')
			print(self.dev_rc, "open")

			ch7 = 0
			st7 = 0
			while self.on:
				d = self.uart.read(16)
				self.ch0, self.ch1, self.ch2, \
				self.ch3, self.ch4, self.ch5, self.ch7, self.ch6, self.ch8, \
				= struct.unpack('HHHHHHBBH', d)

				'''
				if ch3 == 0:
					if self.ch3 == self.cfg.SBUS_CH3_CENTER:
						ch3 = self.ch3
				elif ch3 != self.ch3:
					if self.ch3 == 0x400:
						self.q_button.put([99,'d'])
					else:
						self.q_button.put([99,'D'])
					ch3 = self.ch3
				'''

				if ch7 == 0:
					if self.ch7 == self.cfg.SBUS_CH7_CENTER:
						ch7 = self.ch7
				elif ch7 < self.ch7 and st7 <= 2: # up
					if st7 == -4:
						self.q_button.put([99,'D'])
					elif st7 == -3:
						self.q_button.put([99,'a'])
					elif st7 == -2:
						self.q_button.put([99,'u'])
					elif st7 == -1:
						self.q_button.put([99,'P'])
					elif st7 == 0:
						self.q_button.put([99,'p'])
					elif st7 == 1:
						self.q_button.put([99,'r'])
					elif st7 == 2:
						self.q_button.put([99,'d'])
					ch7 = self.ch7
					st7 = st7 + 1
				elif ch7 > self.ch7 and st7 >= -4: # down
					if st7 == 3:
						self.q_button.put([99,'D'])
					if st7 == 2:
						self.q_button.put([99,'R'])
					elif st7 == 1:
						self.q_button.put([99,'P'])
					elif st7 == 0:
						self.q_button.put([99,'p'])
					elif st7 == -1:
						self.q_button.put([99,'a'])
					elif st7 == -2:
						self.q_button.put([99,'l'])
					elif st7 == -3:
						self.q_button.put([99,'d'])
					elif st7 == -4:
						self.q_button.put([99,'P'])
						self.q_button.put([99,'D'])
					ch7 = self.ch7
					st7 = st7 - 1

	def run_threaded(self):
		rpm = 0
		if self.ch0 != 0:
			rpm = 60 * 1000000 // self.ch0
		return \
			float((self.ch1 - self.ch1center)/((self.ch1max - self.ch1min) / 2)), \
			float((self.ch2 - self.ch2center)/((self.ch2max - self.ch2min) / 2)), \
			rpm, \
			self.ch0, \
			self.ch1, \
			self.ch2, \
			self.ch3, \
			self.ch4, \
			self.ch5, \
			self.ch6, \
			self.ch7, \
			self.ch8

	def shutdown(self):
		self.on = False
