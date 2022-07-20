import os
import time

class Say:

	def __init__(self, cfg):

		self.num = 0
		self.lap = 0
		os.system("aplay ./wav/起動しました.wav &")

	def run(self, mode, num, lap):
	
		if mode == 'user':
			if num and self.num != num // 1000:
				self.num = num // 1000
				os.system("aplay ./wav/data" + str(num) + ".wav &")
			if lap and self.lap != lap:
				self.lap = lap
				os.system("aplay ./wav/lap" + str(abs(lap)) + ".wav &")
