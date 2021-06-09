import time
import RPi.GPIO as GPIO

class BUZZER:

    def __init__(self, cfg):
        self.cfg = cfg
        self.on = True

        GPIO.setmode(GPIO.BOARD)
        self.gpio_pin_buzzer = 36
        GPIO.setup(self.gpio_pin_buzzer, GPIO.OUT)
        GPIO.output(self.gpio_pin_buzzer, GPIO.HIGH)

    def run(self, num_records):
        if type(num_records) == int:
            if num_records < 1000 or num_records > 5000:
                n = num_records % 1000
                if n > 0 and n < 500//self.cfg.DRIVE_LOOP_HZ:
                    GPIO.output(self.gpio_pin_buzzer, GPIO.LOW)
                else:
                    GPIO.output(self.gpio_pin_buzzer, GPIO.HIGH)

    def shutdown(self):
        self.on = False
        GPIO.output(self.gpio_pin_buzzer, GPIO.HIGH)
