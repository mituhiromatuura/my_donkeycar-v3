import time
import queue
import socket
import subprocess

class RfComm:

	def __init__(self, cfg, q_rfcomm):
		self.cfg = cfg
		self.q_rfcomm = q_rfcomm
		self.on = True

		try:
			self.dev_rc = '/dev/rfcomm0'
			self.bt = open(self.dev_rc, 'w')
			print(self.dev_rc, "open")

			host = socket.gethostname()
			print(host)
			self.bt.write("HOSTNAME:" + host + "\n")

			tmp = subprocess.check_output("wpa_cli -i wlan0 status", shell=True).decode()
			idx = tmp.find("bssid=")
			idx0 = tmp.find("ssid=", idx+6)
			idx1 = tmp.find("\n", idx0)
			ssid = tmp[idx0 + 5:idx1]
			print(ssid)
			self.bt.write("SSID:" + ssid + "\n")

			ifconfig = subprocess.check_output("ifconfig", shell=True).decode()
			idx = ifconfig.find("wlan0: ")
			idx0 = ifconfig.find("inet ", idx)
			idx1 = ifconfig.find("  ", idx0)
			ip = ifconfig[idx0 + 5:idx1]
			print(ip)
			self.bt.write("IP:" + ip + "\n")
		except:
			print(self.dev_rc, "none")
			self.on = False

	def update(self):
		while self.on:
			s = self.q_rfcomm.get()
			self.bt.write(s + "\n")

	def run_threaded(self):
		return

	def shutdown(self):
		self.on = False
