import time
import os
import re
import struct

class Wt901c:

	def __init__(self, dev_rc):
		self.on = True
		self.dev_rc = "/dev/ttyMPU9250" #dev_rc
		self.acc = { 'x' : 0., 'y' : 0., 'z' : 0. }
		self.gyro  = { 'x' : 0., 'y' : 0., 'z' : 0. }
		self.mag   = { 'x' : 0., 'y' : 0., 'z' : 0. }
		self.angl  = { 'x' : 0., 'y' : 0., 'z' : 0. }
		self.q     = { '0' : 0., '1' : 0., '2' : 0., '3': 0.}

	def update(self):
		while self.on:
			while not os.path.exists(self.dev_rc):
				#print(self.dev_rc, "is missing")
				time.sleep(2)

			uart = open(self.dev_rc,'r')
			print(self.dev_rc, "open")
			while self.on:
				try:
					s = uart.readline()
					l = re.findall(r"-?\d+(?:\.\d+)?",s)
					if "Acc:" in s:
						self.acc['x'] = float(l[0])
						self.acc['y'] = float(l[1])
						self.acc['z'] = float(l[2])
						#print("Acc:", self.acc['x'], self.acc['y'], self.acc['z'])
					elif "Gyro:" in s:
						self.gyro['x'] = float(l[0])
						self.gyro['y'] = float(l[1])
						self.gyro['z'] = float(l[2])
						#print("Gyro:", self.gyro['x'], self.gyro['y'], self.gyro['z'])
					elif "Mag:" in s:
						self.mag['x'] = float(l[0])
						self.mag['y'] = float(l[1])
						self.mag['z'] = float(l[2])
						#print("Mag:", self.mag['x'], self.mag['y'], self.mag['z'])
					elif "Angle:" in s:
						self.angl['x'] = float(l[0])
						self.angl['y'] = float(l[1])
						self.angl['z'] = float(l[2])
						#print("Angle:", self.angl['x'], self.angl['y'], self.angl['z'])
					elif "Q:" in s:
						self.q['0'] = float(l[0])
						self.q['1'] = float(l[1])
						self.q['2'] = float(l[2])
						self.q['3'] = float(l[3])
						#print("Q:", self.q['0'], self.q['1'], self.q['2'], self.q['3'])

				except:
					print("wt901c error")
					break

	def run_threaded(self):
		return \
			self.acc['x'],  self.acc['y'],  self.acc['z'], \
			self.gyro['x'], self.gyro['y'], self.gyro['z'], \
			self.mag['x'],  self.mag['y'],  self.mag['z'], \
			self.angl['x'], self.angl['y'], self.angl['z'], \
			self.q['0'],    self.q['1'],    self.q['2'],    self.q['3']

	def shutdown(self):
		self.on = False
