import time
import queue

class Buzzer:

	def __init__(self, cfg, q_rfcomm):
		self.cfg = cfg
		self.q_rfcomm = q_rfcomm
		self.on = False

	def run(self, mode, num_records):
		if type(num_records) == int:
			n = num_records % 1000
			if n > 0 and n < 1000//self.cfg.DRIVE_LOOP_HZ:
				if not self.on:
					self.q_rfcomm.put("BZ:" + str(num_records//1000) + "\n")
					self.on = True
			else:
				self.on = False

	def shutdown(self):
		self.on = False
