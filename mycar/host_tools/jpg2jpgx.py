#!/usr/bin/env python3

import sys
import os
import subprocess

if len(sys.argv) != 6:
	#print("jpg2jpgx.py path sec   sec   fps offset")
	print("jpg2jpgx.py path flame flame 1 offset")
else:
	offset = int(sys.argv[5])
	p = "/run/shm/" + sys.argv[1] + "/mycar/data/tubx" + sys.argv[5] + "/"
	print(p)
	e = 1 + offset
	while True:
		fp = p + str(e) + "_cam-image_array_.jpg"
		if not (os.path.exists(fp) or os.path.exists(fp + "x")):
			break
		e = e + 1

	e = e - 1
	print("Max Number:", e)

	fps = int(sys.argv[4])
	start = int(sys.argv[2]) * fps
	end = int(sys.argv[3]) * fps

	if end == 0:
		print("end is ", e)
	elif e <= end:
		print(e, " <= ", end)
	else:
		s = e - end
		print("cut " + str(s) + " to " + str(e - offset))
		print("jpg -> jpgx")

		for n in range(s,e+1 - offset):
			#subprocess.run(
			#	"mv " + p + str(n) + "_cam-image_array_.jpg"
			#	+ " " + p + str(n) + "_cam-image_array_.jpgx"
			#	, shell=True)

			subprocess.run(
				"mv " + p + "record_" + str(n) + ".json"
				+ " " + p + "record_" + str(n) + ".jsonx"
				, shell=True)

	if e <= start:
		print(e, " <= ", start)
	else:
		e = start
		print("cut " + str(1 + offset) + " to " + str(e))
		print("jpg -> jpgx")

		for n in range(1 + offset,e+1):
			#subprocess.run(
			#	"mv " + p + str(n) + "_cam-image_array_.jpg"
			#	+ " " + p + str(n) + "_cam-image_array_.jpgx"
			#	, shell=True)

			subprocess.run(
				"mv " + p + "record_" + str(n) + ".json"
				+ " " + p + "record_" + str(n) + ".jsonx"
				, shell=True)
