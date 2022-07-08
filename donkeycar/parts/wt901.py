import time
import os
import re
import serial
import struct

class Wt901:

	def __init__(self, dev_rc):
		self.on = True
		self.dev_rc = "/dev/ttyWt901" #dev_rc
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

			uart = serial.Serial(self.dev_rc)
			uart.baudrate = 115200
			uart.parity = serial.PARITY_NONE
			uart.bytesize = serial.EIGHTBITS
			uart.stopbits = serial.STOPBITS_ONE
			print(self.dev_rc, "open")

			while self.on:
				try:
					s1 = uart.read(1)
					#print(s)
					if s1 == b'\x55':
						s1 = uart.read(1)
						if s1 == b'\x51':
							s9 = uart.read(9)
							d = struct.unpack('BBBBBBBBB',s9)
							if d[8]==((0x55+0x51+d[0]+d[1]+d[2]+d[3]+d[4]+d[5]+d[6]+d[7])&0xff):
								tmp1,tmp2,tmp3,tmp4,tmp5 = struct.unpack('hhhhb',s9)
								self.acc['x'] = tmp1/32768*16
								self.acc['y'] = tmp2/32768*16
								self.acc['z'] = tmp3/32768*16
								#print("acc:",self.acc['x'],",",self.acc['y'],",",self.acc['z'])
							else:
								print("sum error:acc")

						elif s1 == b'\x52':
							s9 = uart.read(9)
							d = struct.unpack('BBBBBBBBB',s9)
							if d[8]==((0x55+0x52+d[0]+d[1]+d[2]+d[3]+d[4]+d[5]+d[6]+d[7])&0xff):
								tmp1,tmp2,tmp3,tmp4,tmp5 = struct.unpack('hhhhb',s9)
								self.gyro['x'] = tmp1/32768*2000
								self.gyro['y'] = tmp2/32768*2000
								self.gyro['z'] = tmp3/32768*2000
								#print("gyro:",self.gyro['x'],",",self.gyro['y'],",",self.gyro['z'])
							else:
								print("sum error:gyro")

						elif s1 == b'\x53':
							s9 = uart.read(9)
							d = struct.unpack('BBBBBBBBB',s9)
							if d[8]==((0x55+0x53+d[0]+d[1]+d[2]+d[3]+d[4]+d[5]+d[6]+d[7])&0xff):
								tmp1,tmp2,tmp3,tmp4,tmp5 = struct.unpack('hhhhb',s9)
								self.angl['x'] = tmp1/32768*180
								self.angl['y'] = tmp2/32768*180
								self.angl['z'] = tmp3/32768*180
								#print("angl:",self.angl['x'],",",self.angl['y'],",",self.angl['z'])
							else:
								print("sum error:angl")

						elif s1 == b'\x54':
							s9 = uart.read(9)
							d = struct.unpack('BBBBBBBBB',s9)
							if d[8]==((0x55+0x54+d[0]+d[1]+d[2]+d[3]+d[4]+d[5]+d[6]+d[7])&0xff):
								tmp1,tmp2,tmp3,tmp4,tmp5 = struct.unpack('hhhhb',s9)
								self.mag['x'] = tmp1
								self.mag['y'] = tmp2
								self.mag['z'] = tmp3
								#print("mag:",self.mag['x'],",",self.mag['y'],",",self.mag['z'])
							else:
								print("sum error:mag")

						elif s1 == b'\x59':
							s9 = uart.read(9)
							d = struct.unpack('BBBBBBBBB',s9)
							if d[8]==((0x55+0x59+d[0]+d[1]+d[2]+d[3]+d[4]+d[5]+d[6]+d[7])&0xff):
								tmp1,tmp2,tmp3,tmp4,tmp5 = struct.unpack('hhhhb',s9)
								self.q['x'] = tmp1/32768
								self.q['y'] = tmp2/32768
								self.q['z'] = tmp3/32768
								#print("q:",self.q['x'],",",self.q['y'],",",self.q['z'])
							else:
								print("sum error:q")

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
