import time

class Buzzer:

	def __init__(self, cfg):
		self.cfg = cfg
		self.on = True

		try:
			self.dev_rc = '/dev/rfcomm0'
			self.bt = open(self.dev_rc, 'w')
			print(self.dev_rc, "open")
			self.bt.write("START\n")
		except:
			print(self.dev_rc, "none")
		self.on = False

	def run(self, mode, num_records):
		if mode == 'user' and type(num_records) == int:
			n = num_records % 1000
			if n > 0 and n < 1000//self.cfg.DRIVE_LOOP_HZ:
				if not self.on:
					try:
						self.bt.write("BZ:" + str(num_records//1000) + "\n")
					except:
						print(self.dev_rc, "none")
					self.on = True
			else:
				self.on = False

	def shutdown(self):
		self.on = False
