import time
import queue

class Buzzer:

	def __init__(self, cfg, q_rfcomm):
		self.cfg = cfg
		self.q_rfcomm = q_rfcomm
		self.num = -1

	def run(self, mode, num_records):
		if type(num_records) == int:
			n = num_records // 100
			if self.num != n:
				if self.cfg.USE_REM_BUZZER:
					self.q_rfcomm.put("BZ:" + str(n) + "\n")
				else:
					self.q_rfcomm.put("bz:" + str(n) + "\n")
				self.num = n
