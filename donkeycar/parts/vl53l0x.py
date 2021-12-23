import time
import os
import re
import RPi.GPIO as GPIO

class Vl53l0x:

	def __init__(self, dev_rc):
		self.on = True
		self.dev_rc = dev_rc
		self.ad0 = 0
		self.ad1 = 0
		self.ad2 = 0
		self.ad3 = 0
		self.ad4 = 0
		self.ad5 = 0
		self.ad6 = 0
		self.ad7 = 0

		self.gpio_pin = 12 #GPIO18
		GPIO.setup(self.gpio_pin, GPIO.OUT)
		GPIO.output(self.gpio_pin, GPIO.LOW)
		time.sleep(0.5)
		GPIO.output(self.gpio_pin, GPIO.HIGH)
		time.sleep(0.5)

	def update(self):
		while self.on:
			while not os.path.exists(self.dev_rc):
				#print(self.dev_rc, "is missing")
				time.sleep(2)

			self.uart = open(self.dev_rc,'r')
			print(self.dev_rc, "open")
			while self.on:
				try:
					s = self.uart.readline()
					l =  re.findall(r"-?\d+(?:\.\d+)?",s)
					if "0:" in s:
						self.ad0 = int(l[1])
					elif "1:" in s:
						self.ad1 = int(l[1])
					elif "2:" in s:
						self.ad2 = int(l[1])
					elif "3:" in s:
						self.ad3 = int(l[1])
					elif "4:" in s:
						self.ad4 = int(l[1])
					elif "5:" in s:
						self.ad5 = int(l[1])
					elif "6:" in s:
						self.ad6 = int(l[1])
					elif "7:" in s:
						self.ad7 = int(l[1])
				except KeyboardInterrupt:
					self.on = False
					print("KeyboardInterrupt:Vl53l0x")
				except:
					self.on = False
					print(self.dev_rc, " error")
					break

	def conv(self, ad):
		return max(0, 2000 - ad) / 2000

	def run_threaded(self):
		return \
			self.conv(self.ad0), \
			self.ad0

	def shutdown(self):
		self.on = False
