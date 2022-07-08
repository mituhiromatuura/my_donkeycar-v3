import time
import RPi.GPIO as GPIO

class CycleTime:
    def __init__(self, cfg):
        self.cfg = cfg
        self.gpio_pin_cycletime = cfg.GPIO_PIN_BCM_CYCLETIME
        self.led_off = GPIO.HIGH
        self.led_on = GPIO.LOW
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_pin_cycletime, GPIO.OUT)
        GPIO.output(self.gpio_pin_cycletime, self.led_off)

        self.sum = 0
        self.n = 0
        self.time = time.time()

    def run(self, mode):
        cycle = (time.time() - self.time)
        self.time = time.time()

        if 1.0 / self.cfg.DRIVE_LOOP_HZ < cycle:
            GPIO.output(self.gpio_pin_cycletime, self.led_on)

        self.sum += cycle
        self.n += 1
        return cycle * 1000 # msec

    def shutdown(self):
        print("CycleTime avg = ", self.sum / self.n * 1000)
