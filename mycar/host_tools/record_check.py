#!/usr/bin/env python3

import sys
import os
import subprocess
import json
import matplotlib.pyplot as plt

num = list()
user_angle = list()
user_throttle = list()
pilot_angle = list()
pilot_throttle = list()

datapath = (sys.argv[1])
offset = (sys.argv[2])
fps = int(sys.argv[3])
low = float(sys.argv[4])
sec = int(sys.argv[5])
start = int(sys.argv[6])

datapath += offset

p = datapath + "/"
e = start + 1
while True:
	#fp = p + str(e) + "_cam-image_array_.jpg"
	fp = p + "record_" + str(e) + ".json"
	if not (os.path.exists(fp) or os.path.exists(fp + "x")):
		break
	e = e + 1

e = e - 1
print("Max Number:", e)

n = start + 1
while n <= e:
	if True: #try:
		fname = datapath + '/record_' + str(n) + '.json'
		if os.path.isfile(fname):
			f = open(fname, 'r')
			js = json.load(f)

			#print(js)
			#print(js['cam/image_array'])
			#print(js['user/mode'])

			#print(js['user/angle'])
			#print(js['user/throttle'])
			#print(js['pilot/angle'])
			#print(js['pilot/throttle'])

			num.append(int(js['cam/image_array'].split('_')[0]))
			user_angle.append(float(js['user/angle']))
			user_throttle.append(float(js['user/throttle']))
			try:
				pilot_angle.append(float(js['pilot/angle']))
				pilot_throttle.append(float(js['pilot/throttle']))
			except:
				pass

			check = False

			v = float(js['user/throttle'])
			if v < low:
				print("ut ", n, v)
				check = True

			if check:
				for x in range(n - sec * fps, n + sec * fps):
				#for x in range(n - sec * fps, n + 1):
					#print("rename" + str(x));

					#jpeg_name = datapath + "/" + str(x) + "_cam-image_array_"
					json_name = datapath + "/" + "record_" + str(x)

					#if os.path.isfile(jpeg_name + ".jpg"):
					#	subprocess.run(
					#		"mv " + jpeg_name + ".jpg"
					#		+ " " + jpeg_name + ".jpgx"
					#		, shell=True)

					if os.path.isfile(json_name + ".json"):
						subprocess.run(
							"mv " + json_name + ".json"
							+ " " + json_name + ".jsonx"
							, shell=True)

	#except:
	#	pass

	n += 1
