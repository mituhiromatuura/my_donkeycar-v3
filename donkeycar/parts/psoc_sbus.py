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
		self.ch9 = 0
		self.ch10 = 0
		self.ch11 = 0
		self.ch12 = 0
		self.ch13 = 0
		self.ch14 = 0
		self.ch15 = 0
		self.ch16 = 0

		self.q_button.put([99,'P'])
		self.q_button.put([99,'R'])

	def update(self):
		while self.on:
			while not os.path.exists(self.dev_rc):
				#print(self.dev_rc, "is missing")
				time.sleep(2)

			self.uart = open(self.dev_rc,'rb')
			print(self.dev_rc, "open")

			f = open(self.dev_rc,'w')
			f.write("ok")
			f.flush()
			f.close()

			ch7 = 0xff
			st7 = 0
			while self.on:
				d = self.uart.read(16)
				self.ch0, self.ch1, self.ch2, \
				L, H, ch4x, ch5x, ch6x, self.ch8, \
				= struct.unpack('HHHBBHHHH', d)

				if H == 3:
					self.ch3 = L - 100
				elif H == 4:
					self.ch4 = L - 100
				elif H == 5:
					self.ch5 = L - 100
				elif H == 6:
					self.ch6 = L - 100
				elif H == 7:
					self.ch7 = L - 100
				elif H == 7+1:
					self.ch9 = L - 100
				elif H == 7+2:
					self.ch10 = L - 100
				elif H == 7+3:
					self.ch11 = L - 100
				elif H == 7+4:
					self.ch12 = L - 100
				elif H == 7+5:
					self.ch13 = L - 100
				elif H == 7+6:
					self.ch14 = L - 100
				elif H == 7+7:
					self.ch15 = L - 100
				elif H == 7+8:
					self.ch16 = L - 100

				if ch7 == 0xff:
					if self.ch7 == 0:
						ch7 = 0
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
					st7 += 1
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
					st7 -= 1

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
			self.ch8, \
			self.ch9, \
			self.ch10, \
			self.ch11, \
			self.ch12, \
			self.ch13, \
			self.ch14, \
			self.ch15, \
			self.ch16

	def shutdown(self):
		self.on = False
