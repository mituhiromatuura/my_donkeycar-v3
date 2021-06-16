import time
import smbus

class LED:

    def __init__(self, addr=0x40, poll_delay=0.1):
        self.bus = smbus.SMBus(1)
        self.addr = addr
        self.poll_delay = poll_delay
        self.on = True

        self.dev_ok = False
        self.blink_rate = [0.0,0.0,0.0,0.0, 0.0,0.0,0.0,0.0, 0.0,0.0,0.0,0.0, 0.0,0.0,0.0,0.0]
        self.blink_changed = [0.0,0.0,0.0,0.0, 0.0,0.0,0.0,0.0, 0.0,0.0,0.0,0.0, 0.0,0.0,0.0,0.0,]
        self.led_on = [False,False,False,False, False,False,False,False, False,False,False,False, False,False,False,False]

    def update(self):
        while self.on:
            self.poll()
            time.sleep(self.poll_delay)

    def poll(self):
        if not self.dev_ok:
            self.pca_init()
        if self.dev_ok:
            for pin in range(16):
                if self.blink_rate[pin] == 0:
                    self.toggle(False, pin)
                elif self.blink_rate[pin] > 0:
                    self.blink(self.blink_rate[pin], pin, time.time())
                else:
                    self.toggle(True, pin)

    def pca_init(self):
        reg_mode1 = 0x00
        reg_mode2 = 0x01

        try:
            self.bus.write_byte_data(self.addr,reg_mode1,0x01) #ALLCALL
            self.bus.write_byte_data(self.addr,reg_mode2,0x00) #open-drain

            for pin in range(16):
                reg_on_h = pin * 4 + 6 + 1
                reg_off_h = pin * 4 + 6 + 3

                self.bus.write_byte_data(self.addr,reg_on_h,0x10)
                self.bus.write_byte_data(self.addr,reg_off_h,0x00)

            self.dev_ok = True
        except:
            self.dev_ok = False
            #print("PCA9685 missing")

    def toggle(self, condition, pin):
        reg_on_l = pin * 4 + 6 + 0
        reg_on_h = pin * 4 + 6 + 1
        reg_off_l = pin * 4 + 6 + 2
        reg_off_h = pin * 4 + 6 + 3

        try:
            if condition:
                if not self.led_on[pin]:
                    self.bus.write_byte_data(self.addr,reg_on_h,0x00)
                    self.bus.write_byte_data(self.addr,reg_off_h,0x10)
                    self.led_on[pin] = True
            else:
                if self.led_on[pin]:
                    self.bus.write_byte_data(self.addr,reg_on_h,0x10)
                    self.bus.write_byte_data(self.addr,reg_off_h,0x00)
                    self.led_on[pin] = False
        except KeyboardInterrupt:
            self.on = False
            print("KeyboardInterrupt:LED")
        except:
            self.dev_ok = False
            if pin == 0:
                print("PCA9685 missing")

    def blink(self, rate, pin, now):
        if now - self.blink_changed[pin] > rate:
            self.toggle(not self.led_on[pin], pin)
            self.blink_changed[pin] = now

    def run_threaded(self, p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15):
        self.blink_rate = [p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15]

    def run(self, p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15):
        if self.on:
            self.blink_rate = [p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15]
        self.poll()

    def shutdown(self):
        self.on = False
        if self.dev_ok:
            for pin in range(16):
                self.toggle(False, pin)

if __name__ == "__main__":

    p = LED()

    while True:

        p.run(-0.5,0.5,0.5,-0.5, 0.5,0.5,0.5,0.5, 0.5,0.5,0.5,0.5, 0.5,0.5,0.5,0.5)
        time.sleep(0.1)
