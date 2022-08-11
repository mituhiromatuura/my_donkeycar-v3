#!/usr/bin/env python3

import sys
import os
import subprocess

num = list()

datapath = (sys.argv[1])

p1 = datapath + "/"
p2 = datapath + "x" + sys.argv[2] + "/"
e = 1
n = int(sys.argv[2])
while True:
	fp1 = p1 + str(e) + "_cam-image_array_.jpg"
	fp2 = p2 + str(e + n) + "_cam-image_array_.jpg"
	if not (os.path.exists(fp1)):
		break
	subprocess.run("cp " + fp1 + " " + fp2, shell=True)
	e = e + 1

emax = e - 1
print("Max Number:", emax)

e = n + 1
while e <= emax:
	fp1 = p1 + "record_" + str(e) + ".json"
	fp2 = p2 + "record_" + str(e) + ".json"
	if not (os.path.exists(fp1)):
		break
	subprocess.run("cp " + fp1 + " " + fp2, shell=True)
	e = e + 1

print("Max Number:", emax)
