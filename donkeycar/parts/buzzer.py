import time
import RPi.GPIO as GPIO

class Buzzer:

    def __init__(self, cfg):
        self.cfg = cfg
        self.on = True

        GPIO.setmode(GPIO.BOARD)
        self.gpio_pin_buzzer = 36
        GPIO.setup(self.gpio_pin_buzzer, GPIO.OUT)
        GPIO.output(self.gpio_pin_buzzer, GPIO.HIGH)

    def run(self, num_records):
        if type(num_records) == int:
            n = num_records % 1000
            if num_records > 5000 and num_records < 6000:
                if n > 0 and n < 1000//self.cfg.DRIVE_LOOP_HZ:
                    GPIO.output(self.gpio_pin_buzzer, GPIO.LOW)
                else:
                    GPIO.output(self.gpio_pin_buzzer, GPIO.HIGH)
            else:
                if n > 0 and n < 250//self.cfg.DRIVE_LOOP_HZ:
                    GPIO.output(self.gpio_pin_buzzer, GPIO.LOW)
                else:
                    GPIO.output(self.gpio_pin_buzzer, GPIO.HIGH)

    def shutdown(self):
        self.on = False
        GPIO.output(self.gpio_pin_buzzer, GPIO.HIGH)
