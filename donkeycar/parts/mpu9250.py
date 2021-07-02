import time
import os
import re

class Mpu9250:

    def __init__(self, dev_rc):
        self.dev_rc = dev_rc
        self.accel = { 'x' : 0., 'y' : 0., 'z' : 0. }
        self.gyro = { 'x' : 0., 'y' : 0., 'z' : 0. }
        self.mag = {'x': 0., 'y': 0., 'z': 0.}
        self.q = {'0': 0., 'x': 0., 'y': 0., 'z': 0.}
        self.ypr = {'y': 0., 'p': 0., 'r': 0.}
        self.on = True

    def update(self):
        while self.on:
            while not os.path.exists(self.dev_rc):
                #print(self.dev_rc, "is missing")
                time.sleep(2)

            uart = open(self.dev_rc,'r')
            print(self.dev_rc, "open")
            while self.on:
                try:
                    s = uart.readline()
                    l =  re.findall(r"-?\d+(?:\.\d+)?",s)
                    if "ax" in s:
                        self.accel['x'] = float(l[0])
                        self.accel['y'] = float(l[1])
                        self.accel['z'] = float(l[2])
                        #print("acce ", self.accel['x'], self.accel['y'], self.accel['z'])
                    elif "gx" in s:
                        self.gyro['x'] = float(l[0])
                        self.gyro['y'] = float(l[1])
                        self.gyro['z'] = float(l[2])
                        #print("gyro ", self.gyro['x'], self.gyro['y'], self.gyro['z'])
                    elif "mx" in s:
                        self.mag['x'] = float(l[0])
                        self.mag['y'] = float(l[1])
                        self.mag['z'] = float(l[2])
                        #print("mag  ", self.mag['x'], self.mag['y'], self.mag['z'])
                    elif "q0" in s:
                        self.q['0'] = float(l[1])
                        self.q['x'] = float(l[2])
                        self.q['y'] = float(l[3])
                        self.q['z'] = float(l[4])
                        #print("q    ", self.q['0'], self.q['x'], self.q['y'], self.q['z'])
                    elif "Yaw" in s:
                        self.ypr['y'] = float(l[0])
                        self.ypr['p'] = float(l[1])
                        self.ypr['r'] = float(l[2])
                        #print("ypr  ", self.ypr['y'], self.ypr['p'], self.ypr['r'])
                except:
                    print("mpu9250 error")
                    break

    def run_threaded(self):
        return \
            self.accel['x'], self.accel['y'], self.accel['z'], \
            self.gyro['x'], self.gyro['y'], self.gyro['z'], \
            self.mag['x'], self.mag['y'], self.mag['z'], \
            self.q['0'], self.q['x'], self.q['y'], self.q['z'], \
            self.ypr['y'], self.ypr['p'], self.ypr['r']

    def shutdown(self):
        self.on = False

