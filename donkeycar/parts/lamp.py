import os
import time
from donkeycar.parts.led_pca9685 import LED

class LedCtrl:
	def __init__(self, cfg):
		self.cfg = cfg

	def run(self, mode, throttle, rec, const, esc):
		OFF = 0
		ON = -1

		head = OFF
		tail = OFF
		left = OFF
		right = OFF
		blue = OFF
		green = OFF

		if esc:
			head = ON
		if rec:
			tail = ON
		#if throttle < self.cfg.JOYSTICK_DEADZONE:
		if throttle < 0.2:
			left = 0.4
			right = 0.4
		else:
			left = OFF
			right = OFF

		if mode == 'local_angle':
			tail = OFF
			blue = OFF
			green = ON
		elif mode == 'local':
			tail = ON
			blue = ON
			green = OFF
		if const:
			green = ON
		return head, tail, left, right, blue, green
