import time
import queue
import socket
import subprocess
import threading, queue

class RfComm:

	def __init__(self, cfg, q_rfcomm, q_button):
		self.cfg = cfg
		self.q_rfcomm = q_rfcomm
		self.q_button = q_button

		self.dev_rc = '/dev/rfcomm0'
		try:
			self.bt = open(self.dev_rc, 'w')
			print(self.dev_rc, "w open")
			self.ok = True
		except:
			print("rfcomm open error")
			self.ok = False
			return

		self.bt.write("\x1c 1,400,100,2000\n")
		self.bt.write("\x11 3\n")
		self.bt.write("\x12 0\n")

		host = socket.gethostname()
		print(host)
		self.bt.write(host + " 90,180," + str(320-90) + ",20,2\n")

		tmp = subprocess.check_output("wpa_cli -i wlan0 status", shell=True).decode()
		idx = tmp.find("bssid=")
		idx0 = tmp.find("ssid=", idx+6)
		idx1 = tmp.find("\n", idx0)
		ssid = tmp[idx0 + 5:idx1]
		print(ssid)
		self.bt.write(ssid + " 90,200," + str(320-90) + ",20,2\n")

		ifconfig = subprocess.check_output("ifconfig", shell=True).decode()
		idx = ifconfig.find("wlan0: ")
		idx0 = ifconfig.find("inet ", idx)
		idx1 = ifconfig.find("  ", idx0)
		ip = ifconfig[idx0 + 5:idx1]
		print(ip)
		self.bt.write(ip + " 90,220," + str(320-90) + ",20,2\n")

		self.mode = ''
		self.esc_on = True
		self.rec_on = True
		self.ch3 = 1000
		self.ch4 = 1000
		self.ch5 = 1000
		self.ch6 = 1000
		self.num = -1
		self.lap = 1000
		self.va = -1
		self.vb = -1
		self.tnum = time.time()
		self.tva = time.time() + 0.333
		self.tvb = time.time() + 0.666

	def run(self, mode, esc_on, rec_on, ch3, ch4, ch5, ch6, num, lap, va, vb):
		if self.ok:
			try:
				if self.mode != mode:
					self.mode = mode
					self.bt.write(mode + " 0,0,210,30,3\n")
				if self.esc_on != esc_on:
					self.esc_on = esc_on
					if esc_on:
						self.bt.write("ESC_ON 210,0," + str(320-210) + ",30,3," + str(0xf800) + "\n")
					else:
						self.bt.write("ESCOFF 210,0," + str(320-210) + ",30,3," + str(0xffff) + "\n")
				if self.rec_on != rec_on:
					self.rec_on = rec_on
					if rec_on:
						self.bt.write("REC_ON 210,30," + str(320-210) + ",30,3," + str(0xf800) + "\n")
					else:
						self.bt.write("RECOFF 210,30," + str(320-210) + ",30,3," + str(0xffff) + "\n")
				if self.ch3 != ch3:
					self.ch3 = ch3
					self.bt.write(str(ch3) + " 0,30," + str(90) + ",30,3\n")
				if self.ch4 != ch4:
					self.ch4 = ch4
					self.bt.write(str(ch4) + " 0,60," + str(90) + ",30,3\n")
				if self.ch5 != ch5:
					self.ch5 = ch5
					self.bt.write(str(ch5) + " 0,90," + str(90) + ",30,3\n")
				if self.ch6 != ch6:
					self.ch6 = ch6
					self.bt.write(str(ch6) + " 0,120," + str(90) + ",30,3\n")

				if lap is not None and self.lap != lap:
					self.lap = lap
					self.bt.write(str(abs(lap)) + " 90,30," + str(210-90) + ",60,7\n")

				if self.tnum + 1.0 < time.time():
					self.tnum = time.time()
					self.bt.write(str(num) + " 90,90," + str(320-90) + ",60,7\n")

				if self.tvb + 1.0 < time.time():
					self.tvb = time.time()
					self.bt.write("{:.2f}".format(vb) + " 0,180,90,30,3\n")
				if self.tva + 1.0 < time.time():
					self.tva = time.time()
					self.bt.write("{:.2f}".format(va) + " 0,210,90,30,3\n")
			except:
				print("rfcomm write error")
				self.ok = False

	def shutdown(self):
		self.bt.write("\x1c 1,400,100,1000\n")
		self.bt.write("\x12 0\n")
		#self.bt.write("BYE 0,0,0,0,7\n")
		self.bt.write("ABCDEFG 0," + str(  0+8*0) + ",0,0,1," + str(0xf800) + "\n")
		self.bt.write("ABCDEFG 0," + str(  0+8*1) + ",0,0,2," + str(0x07e0) + "\n")
		self.bt.write("ABCDEFG 0," + str(  8+8*2) + ",0,0,3," + str(0x001f) + "\n")
		self.bt.write("ABCDEFG 0," + str( 24+8*3) + ",0,0,4," + str(0xffff) + "\n")
		self.bt.write("ABCDEFG 0," + str( 48+8*4) + ",0,0,5," + str(0xffe0) + "\n")
		self.bt.write("ABCDEFG 0," + str( 80+8*5) + ",0,0,6," + str(0x07ff) + "\n")
		self.bt.write("ABCDEFG 0," + str(120+8*6) + ",0,0,7," + str(0xf81f) + "\n")
		self.bt.close()
