import time
import queue

class Buzzer:

	def __init__(self, cfg, q_rfcomm):
		self.cfg = cfg
		self.q_rfcomm = q_rfcomm
		self.num = -1
		self.deg = 0
		self.lap = 0

	def run(self, esc_on, num_records, period_time, gyr_z):
		if type(num_records) == int:
			n = num_records // 100
			if self.num != n:
				self.q_rfcomm.put(str(n*100) + " 110," + str(30*6) + ",130,30,3\n")
				self.num = n

		if not esc_on:
			self.deg = 0
		else:
			self.deg += period_time * gyr_z
			#print((self.deg / 1000) // 360 , (self.deg / 1000) % 360)
			lap = int(self.deg / 1000 // 360)
			if self.lap != lap:
				print(lap, "lap")
				self.lap = lap
				self.q_rfcomm.put(str(lap) + " 0,240,240,80,10\n")
				#self.q_rfcomm.put("BZ " + str(lap) + ",200,300,0,0\n")
				self.q_rfcomm.put("BZ 1,200,300,0,0\n")

		return self.lap
