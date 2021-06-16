import time

class Log:

	def __init__(self,cfg):

		self.cfg = cfg
		self.on = True

		self.n = -1
		self.sum = 0

		self.num = list()
		self.milliseconds = list()

		self.angle = list()
		self.throttle = list()

		self.user_angle = list()
		self.user_throttle = list()
		self.user_mode = list()

		self.pilot_angle = list()
		self.pilot_throttle = list()

		self.ch1 = list()
		self.ch2 = list()
		self.ch3 = list()
		self.ch4 = list()

		self.acl_x = list()
		self.acl_y = list()
		self.acl_z = list()
		self.gyr_x = list()
		self.gyr_y = list()
		self.gyr_z = list()

		self.volt_a = list()
		self.volt_b = list()

		self.dist0 = list()
		self.dist1 = list()
		self.dist2 = list()
		self.dist3 = list()
		self.dist4 = list()
		self.dist5 = list()
		self.dist6 = list()

	def run(self,
			num,
			milliseconds,

			angle,
			throttle,

			user_angle,
			user_throttle,
			user_mode,

			pilot_angle,
			pilot_throttle,

			ch1,
			ch2,
			ch3,
			ch4,

			acl_x,
			acl_y,
			acl_z,
			gyr_x,
			gyr_y,
			gyr_z,

			volt_a,
			volt_b,

			dist0,
			dist1,
			dist2,
			dist3,
			dist4,
			dist5,
			dist6
			):

		if type(num) == int:
			if self.n != num:
				self.n = num
				self.sum += milliseconds

				self.num.append(num)
				self.milliseconds.append(milliseconds)

				self.angle.append(angle)
				self.throttle.append(throttle)

				self.user_angle.append(user_angle)
				self.user_throttle.append(user_throttle)
				self.user_mode.append(user_mode)

				self.pilot_angle.append(pilot_angle)
				self.pilot_throttle.append(pilot_throttle)

				self.ch1.append(ch1)
				self.ch2.append(ch2)
				self.ch3.append(ch3)
				self.ch4.append(ch4)

				self.acl_x.append(acl_x)
				self.acl_y.append(acl_y)
				self.acl_z.append(acl_z)
				self.gyr_x.append(gyr_x)
				self.gyr_y.append(gyr_y)
				self.gyr_z.append(gyr_z)

				self.volt_a.append(volt_a)
				self.volt_b.append(volt_b)

				self.dist0.append(dist0)
				self.dist1.append(dist1)
				self.dist2.append(dist2)
				self.dist3.append(dist3)
				self.dist4.append(dist4)
				self.dist5.append(dist5)
				self.dist6.append(dist6)

	def shutdown(self):
		self.on = False
		print(self.sum / self.n)

		f = open("/run/shm/mycar/log.csv","w")
		for i in range(self.n):
			f.write(str(self.num[i]))
			f.write(",")
			f.write(str(self.milliseconds[i]))
			f.write(",")
			f.write(str(self.angle[i]))
			f.write(",")
			f.write(str(self.throttle[i]))
			f.write(",")
			f.write(str(self.user_angle[i]))
			f.write(",")
			f.write(str(self.user_throttle[i]))
			f.write(",")
			f.write(    self.user_mode[i])
			f.write(",")
			f.write(str(self.pilot_angle[i]))
			f.write(",")
			f.write(str(self.pilot_throttle[i]))
			f.write(",")
			f.write(str(self.ch1[i]))
			f.write(",")
			f.write(str(self.ch2[i]))
			f.write(",")
			f.write(str(self.ch3[i]))
			f.write(",")
			f.write(str(self.ch4[i]))
			f.write(",")
			f.write(str(self.acl_x[i]))
			f.write(",")
			f.write(str(self.acl_y[i]))
			f.write(",")
			f.write(str(self.acl_z[i]))
			f.write(",")
			f.write(str(self.gyr_x[i]))
			f.write(",")
			f.write(str(self.gyr_y[i]))
			f.write(",")
			f.write(str(self.gyr_z[i]))
			f.write(",")
			f.write(str(self.volt_a[i]))
			f.write(",")
			f.write(str(self.volt_b[i]))
			f.write(",")
			f.write(str(self.dist0[i]))
			f.write(",")
			f.write(str(self.dist1[i]))
			f.write(",")
			f.write(str(self.dist2[i]))
			f.write(",")
			f.write(str(self.dist3[i]))
			f.write(",")
			f.write(str(self.dist4[i]))
			f.write(",")
			f.write(str(self.dist5[i]))
			f.write(",")
			f.write(str(self.dist6[i]))
			f.write("\n")
		f.close()
