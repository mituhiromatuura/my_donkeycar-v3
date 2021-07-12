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

    def run(self, mode, num_records):
        if mode == 'user' and type(num_records) == int:
            if num_records > 5000:
                n = num_records % 1000
                if n > 0 and n < 1000//self.cfg.DRIVE_LOOP_HZ:
                    GPIO.output(self.gpio_pin_buzzer, GPIO.LOW)
                else:
                    GPIO.output(self.gpio_pin_buzzer, GPIO.HIGH)

    def shutdown(self):
        self.on = False
        GPIO.output(self.gpio_pin_buzzer, GPIO.HIGH)
