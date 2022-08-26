DATA_PATH = '/dev/shm/mycar/data'
DRIVE_LOOP_HZ = 80

PINION_GEAR = 18
#PINION_GEAR = 22
#PINION_GEAR = 25
#PINION_GEAR = 27
#SPUR_GEAR = 64
SPUR_GEAR = 68
BEVEL_GEAR = 15
RING_GEAR = 39
TYRE_DIAMETER = 65
GEAR_RATIO = PINION_GEAR / SPUR_GEAR * BEVEL_GEAR / RING_GEAR

GPIO_PIN_BCM_CYCLETIME = 27
GPIO_PIN_BCM_ESC_ON = 23
GPIO_PIN_BCM_TUBWRITER = 5

#HAVE_AHRS = False
HAVE_AHRS = True
#HAVE_INA226 = False
HAVE_INA226 = True

#HAVE_REVCOUNT = False
HAVE_REVCOUNT = True
if HAVE_REVCOUNT:
	REV_RPM_MAX = 15000
	ODOM = (GEAR_RATIO * TYRE_DIAMETER * 3.141592 / 1000)
	KMPH = (GEAR_RATIO * TYRE_DIAMETER * 3.141592 * 60 / 1000 / 1000)

#USE_RFCOMM = False
USE_RFCOMM = True

USE_SAY = False
#USE_SAY = True

PWM_CENTER = 1520
PWM_MIN    = PWM_CENTER-420 #1100
PWM_MAX    = PWM_CENTER+420 #1940

'''
DRIVE_TRAIN_TYPE = "PWM_STEERING_THROTTLE"
if DRIVE_TRAIN_TYPE == "PWM_STEERING_THROTTLE":
	PWM_STEERING_THROTTLE = {
		"PWM_STEERING_PIN": "PCA9685.1:40.1",
		"PWM_STEERING_SCALE": 1.0,
		"PWM_STEERING_INVERTED": False,
		"PWM_THROTTLE_PIN": "PCA9685.1:40.0",
		"PWM_THROTTLE_SCALE": 1.0,
		"PWM_THROTTLE_INVERTED": False,
		"STEERING_LEFT_PWM":    PWM_MIN   /(1000000/4096/(1000/16)),
		"STEERING_RIGHT_PWM":   PWM_MAX   /(1000000/4096/(1000/16)),
		"THROTTLE_FORWARD_PWM": PWM_MAX   /(1000000/4096/(1000/16)),
		"THROTTLE_STOPPED_PWM": PWM_CENTER/(1000000/4096/(1000/16)),
		"THROTTLE_REVERSE_PWM": PWM_MIN   /(1000000/4096/(1000/16)),
	}
'''
DRIVE_TRAIN_TYPE = "PIGPIO_PWM"
if DRIVE_TRAIN_TYPE == "PIGPIO_PWM":
	STEERING_PWM_PIN = 12
	STEERING_PWM_FREQ = 100
	STEERING_PWM_INVERTED = False
	THROTTLE_PWM_PIN = 13
	THROTTLE_PWM_FREQ = 100
	THROTTLE_PWM_INVERTED = False
	STEERING_LEFT_PWM = PWM_MIN * 100
	STEERING_RIGHT_PWM = PWM_MAX * 100
	THROTTLE_FORWARD_PWM = PWM_MAX * 100
	THROTTLE_STOPPED_PWM = PWM_CENTER * 100
	THROTTLE_REVERSE_PWM = PWM_MIN * 100

	LIDAR_PWM_PIN = 19
	LIDAR_PWM_FREQ = 100
	LIDAR_PWM_INVERTED = False
	LIDAR_LEFT_PWM = PWM_MIN * 100
	LIDAR_RIGHT_PWM = PWM_MAX * 100
#'''

HAVE_ODOM = False
#HAVE_ODOM = True
if HAVE_ODOM == True:
	ENCODER_TYPE = 'GPIO'
	MM_PER_TICK = GEAR_RATIO * TYRE_DIAMETER * 3.141592
	ODOM_PIN = 16
	ODOM_DEBUG = False

AUTO_RECORD_ON_THROTTLE = False

'''
CONTROLLER_TYPE = 'F710'
if CONTROLLER_TYPE == 'F710':
	CONTROLLER_ANGLE_NR = 1
	CONTROLLER_THROTTLE_NR = -1
'''
CONTROLLER_TYPE = 'HID16CH'
if CONTROLLER_TYPE == 'HID16CH':
	SBUS_DEVICE = '/dev/hidPsoc'
	SBUS_CH1_CENTER = 1027
	SBUS_CH1_MIN = 304
	SBUS_CH1_MAX = 1744
	SBUS_CH2_CENTER = 1024
	SBUS_CH2_MIN = 1744
	SBUS_CH2_MAX = 304
	SBUS_CHX_CENTER = 0x400
	SBUS_CHX_MIN = 304
	SBUS_CHX_MAX = 1744
	SBUS_CH6_CENTER = 0x80
	SBUS_CH7_CENTER = 0x80
	CONTROLLER_ANGLE_NR = 1
	CONTROLLER_THROTTLE_NR = -1
	PIN_KEYC = 25 #pin22

#HAVE_LIDAR = False
HAVE_LIDAR = True
if HAVE_LIDAR:
	LIDAR_PWM_PIN = 19
	LIDAR_PWM_FREQ = 100
	LIDAR_LEFT_PWM = 1000
	LIDAR_RIGHT_PWM = 2000

USE_SSD1306_128_32 = False
#USE_SSD1306_128_32 = True
if USE_SSD1306_128_32 == True:
	SSD1306_128_32_I2C_ROTATION = 0
	SSD1306_RESOLUTION = 2

RECORD_DURING_AI = True
