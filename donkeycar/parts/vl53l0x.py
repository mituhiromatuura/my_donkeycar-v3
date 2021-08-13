import time
import os
import re

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
				except:
					self.on = False
					print(self.dev_rc, " error")
					break

	def conv(self, ad):
		return max(0, 2000 - ad) / 2000

	def run_threaded(self):
		return \
			self.conv(self.ad0), \
			self.conv(self.ad1), \
			self.conv(self.ad2), \
			self.conv(self.ad3), \
			self.ad0, \
			self.ad1, \
			self.ad2, \
			self.ad3

	def shutdown(self):
		self.on = False
