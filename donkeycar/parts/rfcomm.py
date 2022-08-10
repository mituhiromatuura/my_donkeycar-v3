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

		self.BLACK = 0x0000
		self.RED = 0xf800
		self.GREEN = 0x07e0
		self.BLUE = 0x001f
		self.YELLOW = self.RED + self.GREEN
		self.CYAN = self.GREEN + self.BLUE
		self.MAGENTA = self.BLUE + self.RED
		self.WHITE = self.RED + self.GREEN + self.BLUE

		self.bt.write("\x1c,/kidou.wav\n")
		self.bt.write("\x11,3\n")
		self.bt.write("\x12,0\n")

		host = socket.gethostname()
		print(host)
		self.bt.write(host + "\f,90,180,2\n")

		tmp = subprocess.check_output("wpa_cli -i wlan0 status", shell=True).decode()
		idx = tmp.find("bssid=")
		idx0 = tmp.find("ssid=", idx+6)
		idx1 = tmp.find("\n", idx0)
		ssid = tmp[idx0 + 5:idx1]
		print(ssid)
		self.bt.write(ssid + "\f,90,200,2\n")

		ifconfig = subprocess.check_output("ifconfig", shell=True).decode()
		idx = ifconfig.find("wlan0: ")
		idx0 = ifconfig.find("inet ", idx)
		idx1 = ifconfig.find("  ", idx0)
		ip = ifconfig[idx0 + 5:idx1]
		print(ip)
		self.bt.write(ip + "\f,90,220,2\n")

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
					self.bt.write("{:<11s}".format(mode) + "\f,0,0,3\n")
				if self.esc_on != esc_on:
					self.esc_on = esc_on
					if esc_on:
						self.bt.write("ESC ON\f,212,0,3," + str(self.RED) + "\n")
					else:
						self.bt.write("ESCOFF\f,212,0,3," + str(self.WHITE) + "\n")
				if self.rec_on != rec_on:
					self.rec_on = rec_on
					if rec_on:
						self.bt.write("REC ON\f,212,30,3," + str(self.RED) + "\n")
					else:
						self.bt.write("RECOFF\f,212,30,3," + str(self.WHITE) + "\n")
				if self.ch3 != ch3:
					self.ch3 = ch3
					self.bt.write("{:.2f}".format(ch3) + "\f,0,30,3\n")
				if self.ch4 != ch4:
					self.ch4 = ch4
					self.bt.write("{:.2f}".format(ch4) + "\f,0,60,3\n")
				if self.ch5 != ch5:
					self.ch5 = ch5
					self.bt.write("     \f,0,90,3\n")
					self.bt.write("{:.2f}".format(ch5) + "\f,0,90,3\n")
				if self.ch6 != ch6:
					self.ch6 = ch6
					self.bt.write("{:<3d}".format(ch6) + "\f,0,120,3\n")

				if lap is not None and self.lap != lap:
					self.lap = lap
					self.bt.write(str(abs(lap)) + "\f,90,30,7\n")
					self.bt.write("\x1c,/lap" + str(abs(lap)) + ".wav\n")

				if num is not None and self.num != num // 1000:
					self.num = num // 1000
					self.bt.write("\x1c,/data" + str(self.num) + "000.wav\n")

				if self.tnum + 1.0 < time.time():
					self.tnum = time.time()
					self.bt.write("{:<5s}".format(str(num)) + "\f,90,90,7\n")

				if self.tvb + 1.0 < time.time():
					self.tvb = time.time()
					self.bt.write("{:.2f}".format(vb) + "\f,0,180,3\n")
				if self.tva + 1.0 < time.time():
					self.tva = time.time()
					self.bt.write("{:.2f}".format(va) + "\f,0,210,3\n")
			except:
				print("rfcomm write error")
				self.ok = False

	def shutdown(self):
		self.bt.write("disconnected!\f,0,150,3," + str(self.YELLOW) + "\n")
		self.bt.write("\x1c,/syuuryou.wav\n")
		self.bt.close()
