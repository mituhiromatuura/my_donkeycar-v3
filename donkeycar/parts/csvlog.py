import time

class CsvLog:

	def __init__(self,cfg):

		self.cfg = cfg

		self.n = 0
		self.sum = 0

		self.num = list()
		self.milliseconds = list()

		self.volt_a = list()
		self.volt_b = list()

		self.user_mode = list()
		self.angle = list()
		self.throttle = list()

		self.user_angle = list()
		self.user_throttle = list()

		self.pilot_angle = list()
		self.pilot_throttle = list()

		self.lap = list()
		self.rpm = list()
		self.kmph = list()

		self.throttle_scale = list()
		self.ai_throttle_mult = list()
		self.gyro_gain = list()
		self.stop_range = list()
		self.lidar = list()

		self.acl_x = list()
		self.acl_y = list()
		self.acl_z = list()
		self.gyr_x = list()
		self.gyr_y = list()
		self.gyr_z = list()
		self.mag_x = list()
		self.mag_y = list()
		self.mag_z = list()
		self.angle_x = list()
		self.angle_y = list()
		self.angle_z = list()
		self.q_0 = list()
		self.q_1 = list()
		self.q_2 = list()
		self.q_3 = list()

		self.ch0 = list()
		self.ch1 = list()
		self.ch2 = list()
		self.ch3 = list()
		self.ch4 = list()
		self.ch5 = list()
		self.ch6 = list()
		self.ch7 = list()
		self.ch11 = list()
		self.ch12 = list()
		self.ch13 = list()
		self.ch14 = list()
		self.ch21 = list()
		self.ch22 = list()
		self.ch23 = list()
		self.ch24 = list()

	def run(self,
		num,
		milliseconds,

		volt_a,
		volt_b,

		user_mode,
		angle,
		throttle,

		user_angle,
		user_throttle,

		pilot_angle,
		pilot_throttle,

		rpm,
		kmph,
		lap,

		throttle_scale,
		ai_throttle_mult,
		gyro_gain,
		stop_range,
		lidar,

		acl_x,
		acl_y,
		acl_z,
		gyr_x,
		gyr_y,
		gyr_z,
		mag_x,
		mag_y,
		mag_z,
		angle_x,
		angle_y,
		angle_z,
		q_0,
		q_1,
		q_2,
		q_3,

		ch0,
		ch1,
		ch2,
		ch3,
		ch4,
		ch5,
		ch6,
		ch7,
		ch11,
		ch12,
		ch13,
		ch14,
		ch21,
		ch22,
		ch23,
		ch24,
		):

		if type(num) == int:
			if self.n != num:
				self.n = num
				self.sum += milliseconds

				self.num.append(num)
				self.milliseconds.append(milliseconds)

				self.volt_a.append(volt_a)
				self.volt_b.append(volt_b)

				self.user_mode.append(user_mode)
				self.angle.append(angle)
				self.throttle.append(throttle)

				self.user_angle.append(user_angle)
				self.user_throttle.append(user_throttle)

				self.pilot_angle.append(pilot_angle)
				self.pilot_throttle.append(pilot_throttle)

				self.rpm.append(rpm)
				self.kmph.append(kmph)
				self.lap.append(lap)

				self.throttle_scale.append(throttle_scale)
				self.ai_throttle_mult.append(ai_throttle_mult)
				self.gyro_gain.append(gyro_gain)
				self.stop_range.append(stop_range)
				self.lidar.append(lidar)

				self.acl_x.append(acl_x)
				self.acl_y.append(acl_y)
				self.acl_z.append(acl_z)
				self.gyr_x.append(gyr_x)
				self.gyr_y.append(gyr_y)
				self.gyr_z.append(gyr_z)
				self.mag_x.append(mag_x)
				self.mag_y.append(mag_y)
				self.mag_z.append(mag_z)
				self.angle_x.append(angle_x)
				self.angle_y.append(angle_y)
				self.angle_z.append(angle_z)
				self.q_0.append(q_0)
				self.q_1.append(q_1)
				self.q_2.append(q_2)
				self.q_3.append(q_3)

				self.ch0.append(ch0)
				self.ch1.append(ch1)
				self.ch2.append(ch2)
				self.ch3.append(ch3)
				self.ch4.append(ch4)
				self.ch5.append(ch5)
				self.ch6.append(ch6)
				self.ch7.append(ch7)
				self.ch11.append(ch11)
				self.ch12.append(ch12)
				self.ch13.append(ch13)
				self.ch14.append(ch14)
				self.ch21.append(ch21)
				self.ch22.append(ch22)
				self.ch23.append(ch23)
				self.ch24.append(ch24)

	def shutdown(self):
		if self.n < 1:
			print("no log.csv")
			return

		print("log.csv save start", self.sum / self.n)
		f = open("/run/shm/mycar/data/log.csv","w")
		f.write("n,ms,va,vb,m,a,t,ua,ut,pa,pt,rpm,kmph,lap," + \
				"throttle_scale,ai_throttle_mult,gyro_gain,stop_range,lidar," + \
				"ax,ay,az,gx,gy,gz,mx,my,mz,anx,any,anz,q0,q1,q2,q3," + \
				"ch0,ch1,ch2,ch3,ch4,ch5,ch6,ch7,ch11,ch12,ch13,ch14,ch21,ch22,ch23,ch24\n")
		for i in range(self.n):
			f.write(str(self.num[i]) + ",")
			f.write(str(self.milliseconds[i]) + ",")
			f.write(str(self.volt_a[i]) + ",")
			f.write(str(self.volt_b[i]) + ",")
			f.write(    self.user_mode[i] + ",")
			f.write(str(self.angle[i]) + ",")
			f.write(str(self.throttle[i]) + ",")
			f.write(str(self.user_angle[i]) + ",")
			f.write(str(self.user_throttle[i]) + ",")
			f.write(str(self.pilot_angle[i]) + ",")
			f.write(str(self.pilot_throttle[i]) + ",")
			f.write(str(self.rpm[i]) + ",")
			f.write(str(self.kmph[i]) + ",")
			f.write(str(self.lap[i]) + ",")
			f.write(str(self.throttle_scale[i]) + ",")
			f.write(str(self.ai_throttle_mult[i]) + ",")
			f.write(str(self.gyro_gain[i]) + ",")
			f.write(str(self.stop_range[i]) + ",")
			f.write(str(self.lidar[i]) + ",")
			f.write(str(self.acl_x[i]) + ",")
			f.write(str(self.acl_y[i]) + ",")
			f.write(str(self.acl_z[i]) + ",")
			f.write(str(self.gyr_x[i]) + ",")
			f.write(str(self.gyr_y[i]) + ",")
			f.write(str(self.gyr_z[i]) + ",")
			f.write(str(self.mag_x[i]) + ",")
			f.write(str(self.mag_y[i]) + ",")
			f.write(str(self.mag_z[i]) + ",")
			f.write(str(self.angle_x[i]) + ",")
			f.write(str(self.angle_y[i]) + ",")
			f.write(str(self.angle_z[i]) + ",")
			f.write(str(self.q_0[i]) + ",")
			f.write(str(self.q_1[i]) + ",")
			f.write(str(self.q_2[i]) + ",")
			f.write(str(self.q_3[i]) + ",")
			f.write(str(self.ch0[i]) + ",")
			f.write(str(self.ch1[i]) + ",")
			f.write(str(self.ch2[i]) + ",")
			f.write(str(self.ch3[i]) + ",")
			f.write(str(self.ch4[i]) + ",")
			f.write(str(self.ch5[i]) + ",")
			f.write(str(self.ch6[i]) + ",")
			f.write(str(self.ch7[i]) + ",")
			f.write(str(self.ch11[i]) + ",")
			f.write(str(self.ch12[i]) + ",")
			f.write(str(self.ch13[i]) + ",")
			f.write(str(self.ch14[i]) + ",")
			f.write(str(self.ch21[i]) + ",")
			f.write(str(self.ch22[i]) + ",")
			f.write(str(self.ch23[i]) + ",")
			f.write(str(self.ch24[i]) + ",")
			f.write("\n")
		f.close()
		print("log.csv save end")
