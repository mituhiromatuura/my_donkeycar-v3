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
		self.on = True

		tmp = subprocess.check_output("printenv RFCOMM_MAC", shell=True).decode('ascii')
		subprocess.call("sudo rfcomm --raw connect 0 " + tmp.strip() + " 1 &", shell=True)
		time.sleep(1)

		try:
			self.dev_rc = '/dev/rfcomm0'
			self.bt = open(self.dev_rc, 'w')
			print(self.dev_rc, "w open")

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

			threading.Thread(target=self.bt_rx).start()
		except:
			print(self.dev_rc, "none")
			self.on = False

	def update(self):
		try:
			while self.on:
				s = self.q_rfcomm.get()
				self.bt.write(s + "\n")
		except:
			print(self.dev_rc, "none(tx)")
			self.on = False

	def run_threaded(self):
		return

	def shutdown(self):
		self.on = False

	def bt_rx(self):
		try:
			bt = open(self.dev_rc, 'r')
			print(self.dev_rc, "r open")
			while self.on:
				s = bt.readline()
				#print(s.encode())
				if len(s) < 3:
					break
				self.q_button.put([0,s])
		except:
			pass
		print(self.dev_rc, "none(rx)")
		self.on = False
		print(self.dev_rc, "bt_rx() end")
