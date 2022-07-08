import os
import array
import time
import struct
import RPi.GPIO as GPIO
import queue

class SbusHid16ch:

	def __init__(self, cfg, debug=False):

		self.cfg = cfg

		self.mode = 'user'
		self.recording = False
		self.esc_on = False
		self.disp_on = True

		self.dev = cfg.SBUS_DEVICE

		self.ch1center = cfg.SBUS_CH1_CENTER
		self.ch1max = cfg.SBUS_CH1_MAX
		self.ch1min = cfg.SBUS_CH1_MIN
		self.ch2center = cfg.SBUS_CH2_CENTER
		self.ch2max = cfg.SBUS_CH2_MAX
		self.ch2min = cfg.SBUS_CH2_MIN

		self.gpio_pin_esc_on = cfg.GPIO_PIN_BCM_ESC_ON
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.gpio_pin_esc_on, GPIO.OUT)
		GPIO.output(self.gpio_pin_esc_on, GPIO.LOW)

		self.ch0 = 0
		self.ch1 = 0
		self.ch2 = 0
		self.ch3 = 0
		self.ch4 = 0
		self.ch5 = 0
		self.ch6 = 0
		self.ch7 = 0
		self.ch8 = 0
		self.ch11 = 0
		self.ch12 = 0
		self.ch13 = 0
		self.ch14 = 0
		self.ch21 = 0
		self.ch22 = 0
		self.ch23 = 0
		self.ch24 = 0

		try:
			self.uart = open(self.dev,'rb')
			print(self.dev, "open")

			f = open(self.dev,'w')
			f.write("ok")
			f.flush()
			f.close()

			self.on = True
		except:
			print("SbusHid16ch", self.dev, "error")
			self.on = False

	def update(self):

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
				self.ch11 = L - 100
			elif H == 7+2:
				self.ch12 = L - 100
			elif H == 7+3:
				self.ch13 = L - 100
			elif H == 7+4:
				self.ch14 = L - 100
			elif H == 7+5:
				self.ch21 = L - 100
			elif H == 7+6:
				self.ch22 = L - 100
			elif H == 7+7:
				self.ch23 = L - 100
			elif H == 7+8:
				self.ch24 = L - 100

			if ch7 == 0xff:
				if self.ch7 == 0:
					ch7 = 0
			else:
				if self.ch7 == 0 or self.ch7 <= -8:
					self.esc_on = False
					GPIO.output(self.gpio_pin_esc_on, GPIO.LOW)
				else:
					self.esc_on = True
					GPIO.output(self.gpio_pin_esc_on, GPIO.HIGH)

				if self.ch7 == 4:
					self.recording = True
				else:
					self.recording = False

				if self.ch7 == -2:
					self.mode = 'local_angle'
				elif self.ch7 == -4 or self.ch7 == -6:
					self.mode = 'local'
				else:
					self.mode = 'user'

				if self.ch7 == -4:
					if self.disp_on == True:
						print("disp_off")
					self.disp_on = False
				else:
					if self.disp_on == False:
						print("disp_on")
					self.disp_on = True

	def run_threaded(self):

		if not self.on:
			print("SbusHid16ch ", self.dev, " error")

		rpm = 0
		if self.cfg.HAVE_REVCOUNT:
			if self.ch0 != 0:
				rpm = 60 * 1000000 // self.ch0
				if rpm > self.cfg.REV_RPM_MAX:
					rpm = 0

		return \
			float((self.ch1 - self.ch1center) \
				/ ((self.ch1max - self.ch1min) / 2)), \
			float((self.ch2 - self.ch2center) \
				/ ((self.ch2max - self.ch2min) / 2)), \
			self.mode, \
			self.recording, \
			self.esc_on, \
			self.disp_on, \
			rpm, \
			self.ch0, \
			self.ch1, \
			self.ch2, \
			round(self.ch3 / 100 + 1.0, 2), \
			round(self.ch4 / 100 + 1.0, 2), \
			round(self.ch5 / 100, 2), \
			self.ch6 + 100, \
			self.ch7, \
			self.ch8, \
			self.ch11, \
			self.ch12, \
			self.ch13, \
			self.ch14, \
			self.ch21, \
			self.ch22, \
			self.ch23, \
			self.ch24

	def shutdown(self):

		self.on = False
		print("shutdown SbusHid16ch")
