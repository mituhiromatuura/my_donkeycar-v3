
import os
import array
import time
import struct
import random
from threading import Thread
import logging

import threading, queue
import RPi.GPIO as GPIO
from donkeycar.parts.fram import Fram
from donkeycar.parts.spi import Spi

class Joystick(object):
    '''
    An interface to a physical joystick
    '''
    def __init__(self, dev_fn='/dev/input/js0'):
        self.axis_states = {}
        self.button_states = {}
        self.axis_names = {}
        self.button_names = {}
        self.axis_map = []
        self.button_map = []
        self.jsdev = None
        self.dev_fn = dev_fn


    def init(self):
        try:
            from fcntl import ioctl
        except ModuleNotFoundError:
            self.num_axes = 0
            self.num_buttons = 0
            print("no support for fnctl module. joystick not enabled.")
            return False

        if not os.path.exists(self.dev_fn):
            print(self.dev_fn, "is missing")
            return False

        '''
        call once to setup connection to device and map buttons
        '''
        # Open the joystick device.
        print('Opening %s...' % self.dev_fn)
        self.jsdev = open(self.dev_fn, 'rb')

        if (self.dev_fn == '/dev/rfcomm0'):
            return True

        # Get the device name.
        buf = array.array('B', [0] * 64)
        ioctl(self.jsdev, 0x80006a13 + (0x10000 * len(buf)), buf) # JSIOCGNAME(len)
        self.js_name = buf.tobytes().decode('utf-8')
        print('Device name: %s' % self.js_name)

        # Get number of axes and buttons.
        buf = array.array('B', [0])
        ioctl(self.jsdev, 0x80016a11, buf) # JSIOCGAXES
        self.num_axes = buf[0]

        buf = array.array('B', [0])
        ioctl(self.jsdev, 0x80016a12, buf) # JSIOCGBUTTONS
        self.num_buttons = buf[0]

        # Get the axis map.
        buf = array.array('B', [0] * 0x40)
        ioctl(self.jsdev, 0x80406a32, buf) # JSIOCGAXMAP

        for axis in buf[:self.num_axes]:
            axis_name = self.axis_names.get(axis, 'unknown(0x%02x)' % axis)
            self.axis_map.append(axis_name)
            self.axis_states[axis_name] = 0.0
            #print('axis', '0x%03x' % axis, 'name', axis_name)

        # Get the button map.
        buf = array.array('H', [0] * 200)
        ioctl(self.jsdev, 0x80406a34, buf) # JSIOCGBTNMAP

        for btn in buf[:self.num_buttons]:
            btn_name = self.button_names.get(btn, 'unknown(0x%03x)' % btn)
            self.button_map.append(btn_name)
            self.button_states[btn_name] = 0
            print('btn', '0x%03x' % btn, 'name', btn_name)

        return True


    def show_map(self):
        '''
        list the buttons and axis found on this joystick
        '''
        print ('%d axes found: %s' % (self.num_axes, ', '.join(self.axis_map)))
        print ('%d buttons found: %s' % (self.num_buttons, ', '.join(self.button_map)))


    def poll(self):
        '''
        query the state of the joystick, returns button which was pressed, if any,
        and axis which was moved, if any. button_state will be None, 1, or 0 if no changes,
        pressed, or released. axis_val will be a float from -1 to +1. button and axis will
        be the string label determined by the axis map in init.
        '''
        button = None
        button_state = None
        axis = None
        axis_val = None

        if self.jsdev is None:
            return button, button_state, axis, axis_val

        # Main event loop
        evbuf = self.jsdev.read(8)
        #print(evbuf)

        if evbuf:
            tval, value, typev, number = struct.unpack('IhBB', evbuf)
            #print(tval, value, typev, number)

            if typev & 0x80:
                #ignore initialization event
                return button, button_state, axis, axis_val

            if typev & 0x01:
                button = self.button_map[number]
                #print(tval, value, typev, number, button, 'pressed')
                if button:
                    self.button_states[button] = value
                    button_state = value
                    logging.info("button: %s state: %d" % (button, value))

            if typev & 0x02:
                axis = self.axis_map[number]
                #print(tval, value, typev, number, axis, 'axis')
                if axis:
                    fvalue = value / 32767.0
                    self.axis_states[axis] = fvalue
                    axis_val = fvalue
                    logging.debug("axis: %s val: %f" % (axis, fvalue))

        return button, button_state, axis, axis_val


class JoystickController(object):
    '''
    JoystickController is a base class. You will not use this class directly,
    but instantiate a flavor based on your joystick type. See classes following this.

    Joystick client using access to local physical input. Maps button
    presses into actions and takes action. Interacts with the Donkey part
    framework.
    '''


    def __init__(self, poll_delay=0.0,
                 throttle_scale=1.0,
                 steering_scale=1.0,
                 throttle_dir=-1.0,
                 dev_fn='/dev/input/js0',
                 disp_on = True,
                 VTXPower_value = -1.0,
                 auto_record_on_throttle=True):

        self.angle = 0.0
        self.throttle = 0.0
        self.mode = 'user'
        self.poll_delay = poll_delay
        self.running = True
        self.last_throttle_axis_val = 0
        #self.throttle_scale = throttle_scale
        self.steering_scale = steering_scale
        self.throttle_dir = throttle_dir
        self.recording = False
        self.constant_throttle = False
        self.auto_record_on_throttle = auto_record_on_throttle
        self.dev_fn = dev_fn
        self.js = None
        self.tub = None
        self.dead_zone = 0.0

        self.button_down_trigger_map = {}
        self.button_up_trigger_map = {}
        self.axis_trigger_map = {}
        self.init_trigger_maps()

        self.disp_on = disp_on
        self.VTXPower_value = VTXPower_value
        self.esc_on = False
        self.sw_l3 = False
        self.sw_r3 = False

        self.fram = Fram()
        self.throttle_scale, self.have_fram = self.fram.read(0)
        if self.have_fram:
            self.ai_throttle_mult, tmp = self.fram.read(1)
        else:
            self.throttle_scale = 1.0
            self.ai_throttle_mult = 1.0

        self.ch1 = 0
        self.ch2 = 0
        self.ch3 = 0
        self.ch4 = 0

        self.lat1 = False
        self.lat2 = False
        self.lat3 = False

    def init_js(self):
        '''
        Attempt to init joystick. Should be definied by derived class
        Should return true on successfully created joystick object
        '''
        raise(Exception("Subclass needs to define init_js"))


    def init_trigger_maps(self):
        '''
        Creating mapping of buttons to functions.
        Should be definied by derived class
        '''
        raise(Exception("init_trigger_maps"))


    def set_deadzone(self, val):
        '''
        sets the minimim throttle for recording
        '''
        self.dead_zone = val


    def print_controls(self):
        '''
        print the mapping of buttons and axis to functions
        '''
        pt = PrettyTable()
        pt.field_names = ["control", "action"]
        for button, control in self.button_down_trigger_map.items():
            pt.add_row([button, control.__name__])
        for axis, control in self.axis_trigger_map.items():
            pt.add_row([axis, control.__name__])
        print("Joystick Controls:")
        print(pt)

        # print("Joystick Controls:")
        # print("On Button Down:")
        # print(self.button_down_trigger_map)
        # print("On Button Up:")
        # print(self.button_up_trigger_map)
        # print("On Axis Move:")
        # print(self.axis_trigger_map)


    def set_button_down_trigger(self, button, func):
        '''
        assign a string button descriptor to a given function call
        '''
        self.button_down_trigger_map[button] = func


    def set_button_up_trigger(self, button, func):
        '''
        assign a string button descriptor to a given function call
        '''
        self.button_up_trigger_map[button] = func


    def set_axis_trigger(self, axis, func):
        '''
        assign a string axis descriptor to a given function call
        '''
        self.axis_trigger_map[axis] = func


    def set_tub(self, tub):
        self.tub = tub


    def on_throttle_changes(self):
        '''
        turn on recording when non zero throttle in the user mode.
        '''
        #if self.auto_record_on_throttle:
        #    #self.recording = (abs(self.throttle) > self.dead_zone and self.mode == 'user')
        #    self.recording  = (    self.throttle  > self.dead_zone * self.throttle_scale and self.mode == 'user')


    def update(self):
        '''
        poll a joystick for input events
        '''

        #wait for joystick to be online
        while self.running and self.js is None and not self.init_js():
            time.sleep(3)

        while self.running:
            button, button_state, axis, axis_val = self.js.poll()

            if axis is not None and axis in self.axis_trigger_map:
                '''
                then invoke the function attached to that axis
                '''
                self.axis_trigger_map[axis](axis_val)

            if button and button_state >= 1 and button in self.button_down_trigger_map:
                '''
                then invoke the function attached to that button
                '''
                self.button_down_trigger_map[button]()

            if button and button_state == 0 and button in self.button_up_trigger_map:
                '''
                then invoke the function attached to that button
                '''
                self.button_up_trigger_map[button]()

            time.sleep(self.poll_delay)


    def set_steering(self, axis_val):

        self.angle = self.steering_scale * axis_val
        #print("angle", self.angle)


    def set_throttle(self, axis_val):

        #this value is often reversed, with positive value when pulling down
        self.last_throttle_axis_val = axis_val
        self.throttle = (self.throttle_dir * axis_val * self.throttle_scale)
        #print("throttle", self.throttle)
        self.on_throttle_changes()


    def set_ai_throttle_mult(self, axis_val):
        if axis_val > 0 and self.ai_throttle_mult > 0.0:
            self.ai_throttle_mult = round(self.ai_throttle_mult - 0.1, 1)
            print("ai_throttle_mult", self.ai_throttle_mult)
            if self.have_fram:
                self.fram.write(1, self.ai_throttle_mult)
        elif axis_val < 0 and self.ai_throttle_mult < 2.0:
            self.ai_throttle_mult = round(self.ai_throttle_mult + 0.1, 1)
            print("ai_throttle_mult", self.ai_throttle_mult)
            if self.have_fram:
                self.fram.write(1, self.ai_throttle_mult)


    def toggle_manual_recording(self):
        '''
        toggle recording on/off
        '''
        '''
        if self.auto_record_on_throttle:
            print('auto record on throttle is enabled.')
        elif self.recording:
            self.recording = False
        else:
            self.recording = True

        print('recording:', self.recording)
        '''
        if self.auto_record_on_throttle:
            self.auto_record_on_throttle = False
        else:
            self.auto_record_on_throttle = True
        self.recording = False
        print('auto_record_on_throttle:', self.auto_record_on_throttle)


    def increase_max_throttle(self):
        '''
        increase throttle scale setting
        '''
        self.throttle_scale = round(min(1.0, self.throttle_scale + 0.01), 2)
        if self.constant_throttle:
            self.throttle = self.throttle_scale
            self.on_throttle_changes()
        else:
            self.throttle = (self.throttle_dir * self.last_throttle_axis_val * self.throttle_scale)

        print('throttle_scale:', self.throttle_scale)
        if self.have_fram:
            self.fram.write(0, self.throttle_scale)


    def decrease_max_throttle(self):
        '''
        decrease throttle scale setting
        '''
        self.throttle_scale = round(max(0.0, self.throttle_scale - 0.01), 2)
        if self.constant_throttle:
            self.throttle = self.throttle_scale
            self.on_throttle_changes()
        else:
            self.throttle = (self.throttle_dir * self.last_throttle_axis_val * self.throttle_scale)

        print('throttle_scale:', self.throttle_scale)
        if self.have_fram:
            self.fram.write(0, self.throttle_scale)


    def increase_max_throttle_10(self):
        '''
        increase throttle scale setting
        '''
        self.throttle_scale = round(min(2.0, self.throttle_scale + 0.1), 2)
        if self.constant_throttle:
            self.throttle = self.throttle_scale
            self.on_throttle_changes()
        else:
            self.throttle = (self.throttle_dir * self.last_throttle_axis_val * self.throttle_scale)

        print('throttle_scale:', self.throttle_scale)
        if self.have_fram:
            self.fram.write(0, self.throttle_scale)


    def decrease_max_throttle_10(self):
        '''
        decrease throttle scale setting
        '''
        self.throttle_scale = round(max(0.0, self.throttle_scale - 0.1), 2)
        if self.constant_throttle:
            self.throttle = self.throttle_scale
            self.on_throttle_changes()
        else:
            self.throttle = (self.throttle_dir * self.last_throttle_axis_val * self.throttle_scale)

        print('throttle_scale:', self.throttle_scale)
        if self.have_fram:
            self.fram.write(0, self.throttle_scale)


    '''
    def disp_sw_on(self):
        self.disp_on = True
        print('disp_on:', self.disp_on)


    def disp_sw_off(self):
        self.disp_on = False
        print('disp_on:', self.disp_on)
    '''


    def disp_sw_toggle(self):
        if self.disp_on:
            self.disp_on = False
        else:
            self.disp_on = True
        print('disp_sw_toggle:', self.disp_on)


    def esc_sw_on(self):
        self.esc_on = True
        print('esc_on:', self.esc_on)


    def esc_sw_off(self):
        self.esc_on = False
        print('esc_on:', self.esc_on)


    def esc_sw_toggle(self):
        if self.esc_on:
            self.esc_on = False
        else:
            self.esc_on = True
        print('esc_sw_toggle:', self.esc_on)


    def sw_l3_toggle(self):
        if self.sw_l3:
            self.sw_l3 = False
        else:
            self.sw_l3 = True
        print('toggle_l3:', self.sw_l3)


    def sw_r3_toggle(self):
        if self.sw_r3:
            self.sw_r3 = False
        else:
            self.sw_r3 = True
        print('toggle_r3:', self.sw_r3)


    def toggle_constant_throttle(self):
        '''
        toggle constant throttle
        '''
        if self.angle < 0.01:
            if self.constant_throttle:
                self.constant_throttle = False
                self.throttle = 0
                self.on_throttle_changes()
            else:
                self.constant_throttle = True
                self.throttle = self.throttle_scale
                self.on_throttle_changes()
            print('constant_throttle:', self.constant_throttle)


    def toggle_mode(self):
        '''
        switch modes from:
        user: human controlled steer and throttle
        local_angle: ai steering, human throttle
        local: ai steering, ai throttle
        '''
        if self.mode == 'user':
            if abs(self.throttle) < 0.1:
                self.mode = 'local_angle'
        elif self.mode == 'local_angle':
            self.mode = 'local'
        else:
            self.mode = 'user'
        print('new mode:', self.mode)


    def run_threaded(self, img_arr=None):
        self.img_arr = img_arr

        return self.angle, self.throttle, self.mode, self.recording, \
               self.ch1, self.ch2, self.ch3, self.ch4, \
               self.auto_record_on_throttle, \
               self.constant_throttle, \
               self.throttle_scale, \
               self.ai_throttle_mult, \
               self.disp_on, \
               self.esc_on, \
               self.sw_l3, \
               self.sw_r3, \
               self.VTXPower_value, \
               self.lat1, \
               self.lat2, \
               self.lat3


    def run(self, img_arr=None):
        raise Exception("We expect for this part to be run with the threaded=True argument.")
        return None, None, None, None


    def shutdown(self):
        #set flag to exit polling thread, then wait a sec for it to leave
        self.running = False
        time.sleep(0.5)


class TTUJoystickController(JoystickController):
    '''
    A Controller object that maps inputs to actions
    '''
    def __init__(self, *args, **kwargs):
        super(TTUJoystickController, self).__init__(*args, **kwargs)

        self.spi = Spi()

        GPIO.setmode(GPIO.BOARD)

        self.gpio_pin_buzzer = 36 #GPIO20
        GPIO.setup(self.gpio_pin_buzzer, GPIO.OUT)
        GPIO.output(self.gpio_pin_buzzer, GPIO.LOW)

        self.gpio_pin_esc_on = 16 #GPIO23 22 #GPIO25
        GPIO.setup(self.gpio_pin_esc_on, GPIO.OUT)
        GPIO.output(self.gpio_pin_esc_on, GPIO.LOW)

        self.gpio_pin_fpga_reset = 12
        GPIO.setup(self.gpio_pin_fpga_reset, GPIO.OUT)
        GPIO.output(self.gpio_pin_fpga_reset, GPIO.HIGH)

        self.gpio_pin_bec_in = 38 #GPIO20
        GPIO.setup(self.gpio_pin_bec_in, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.becst = 0

        gpio_pin_int = 40
        GPIO.setup(gpio_pin_int, GPIO.IN, GPIO.PUD_DOWN)
        GPIO.add_event_detect(gpio_pin_int, GPIO.RISING)
        GPIO.add_event_callback(gpio_pin_int, self.callback)

    def callback(self, channel):
        GPIO.setmode(GPIO.BOARD)
        if self.esc_on:
            if self.becst == 0:
                GPIO.output(self.gpio_pin_esc_on, GPIO.HIGH)
                if GPIO.input(self.gpio_pin_bec_in):
                    print("bec off")
                    GPIO.output(self.gpio_pin_esc_on, GPIO.LOW)
                    self.becst = 1
            else:
                GPIO.output(self.gpio_pin_esc_on, GPIO.HIGH)
                self.becst = self.becst + 1
                if self.becst == 10:
                    self.becst = 0
        else:
            GPIO.output(self.gpio_pin_esc_on, GPIO.LOW)
            self.becst = 0

        self.ch1, self.ch2, self.ch3, self.ch4 = self.spi.run(self.esc_on)

        pwm_mid = 1530
        pwm_sub = 430
        pwm_min = pwm_mid - pwm_sub
        pwm_max = pwm_mid + pwm_sub

        if (self.ch1 >= pwm_min) and (self.ch1 <= pwm_max):
            self.angle = (self.ch1 - pwm_mid)/pwm_sub # Left -1 0 +1 Right
        self.set_steering(self.angle)

        pwm_mid = 1530
        pwm_sub = 430
        pwm_min = pwm_mid - pwm_sub
        pwm_max = pwm_mid + pwm_sub

        if (self.ch2 >= pwm_min) and (self.ch2 <= pwm_max):
            self.throttle = (pwm_mid - self.ch2)/pwm_sub # Forward 1 0 -1 Reverse
        self.set_throttle(self.throttle)

        self.ch3 = 0

        if self.ch4 != 0:
            self.ch4 = 60 * 1000000 // self.ch4


    def init_js(self):
        '''
        attempt to init joystick
        '''
        return True


    def init_trigger_maps(self):
        '''
        init set of mapping from buttons to function calls for ps4
        '''

        self.button_down_trigger_map = {
        }

        self.axis_trigger_map = {
        }

    def decrease_ai_throttle_mult(self):
        self.ai_throttle_mult = round(self.ai_throttle_mult - 0.1, 1)
        print("ai_throttle_mult", self.ai_throttle_mult)
        if self.have_fram:
            self.fram.write(1, self.ai_throttle_mult)

    def inclease_ai_throttle_mult(self):
        self.ai_throttle_mult = round(self.ai_throttle_mult + 0.1, 1)
        print("ai_throttle_mult", self.ai_throttle_mult)
        if self.have_fram:
            self.fram.write(1, self.ai_throttle_mult)

    def ft230x(self, dev_rc, name, q):
        import pigpio
        pi = pigpio.pi()
        while True:
            while not os.path.exists(dev_rc):
                #print(dev_rc, "is missing")
                time.sleep(2)

            uart = pi.serial_open(dev_rc, 115200, 0)
            print(dev_rc, "open")
            while True:
                try:
                    (n,e) = pi.serial_read(uart)
                except:
                    break
                if n > 0:
                    q.put((name,n,e))
            print(dev_rc, "is missing")

    def jsx(self, dev_rc, name, q):
        while True:
            while not os.path.exists(dev_rc):
                #print(dev_rc, "is missing")
                time.sleep(2)

            rcdev = open(dev_rc, 'rb')
            print(dev_rc, "open")
            while True:
                try:
                    e = rcdev.read(8)
                except:
                    break
                if e:
                    d = struct.unpack('hhhh', e)
                    q.put((name,) + d)
            print(dev_rc, "is missing")

    def lat(self, dev_rc, name, q):
        while True:
            while not os.path.exists(dev_rc):
                #print(dev_rc, "is missing")
                time.sleep(2)

            rcdev = open(dev_rc, 'rb')
            print(dev_rc, "open")
            q.put((name,) + (1,0,0,0,0,0,0,0))
            while True:
                try:
                    e = rcdev.read(16)
                    if e:
                        d = struct.unpack('hhhhhhhh', e)
                        if(d[4] == 1):
                            #print(name, d[4], d[5], d[6], d[7])
                            q.put((name,) + d)
                except:
                    break
            print(dev_rc, "is missing")
            q.put((name,) + (0,0,0,0,0,0,0,0))

    def update(self):
        q = queue.Queue()
        threading.Thread(target=self.lat, args=('/dev/LAT-RC01-1',1,q)).start()
        threading.Thread(target=self.lat, args=('/dev/LAT-RC01-2',2,q)).start()
        threading.Thread(target=self.lat, args=('/dev/LAT-RC01-3',3,q)).start()
        while True:
            d = q.get()
            #print(d,type(d))
            bz = True
            if (d[0] == 1):
                if(d[1] == 0):
                    self.lat1 = False
                elif(d[1] == 1):
                    self.lat1 = True
                elif(d[6] == 115 and d[7] == 0): #[+]
                    self.esc_sw_on()
                elif(d[6] == 165 and d[7] == 0): #[<]
                    self.esc_sw_off()
                elif(d[6] == 163 and d[7] == 0): #[>]
                    self.auto_record_on_throttle = True
                    #self.recording = False
                    self.recording = True
                    print('auto_record_on_throttle:', self.auto_record_on_throttle)
                elif(d[6] == 114 and d[7] == 0): #[-]
                    self.auto_record_on_throttle = False
                    self.recording = False
                    print('auto_record_on_throttle:', self.auto_record_on_throttle)
                elif(d[6] == 164 and d[7] == 0): #[||]
                    self.esc_sw_off()
                    self.auto_record_on_throttle = False
                    self.recording = False
                    self.mode = 'user'
                    self.constant_throttle = False
                    self.throttle = 0
                    self.on_throttle_changes()
                else:
                    bz = False

            elif (d[0] == 2):
                if(d[1] == 0):
                    self.lat2 = False
                elif(d[1] == 1):
                    self.lat2 = True
                elif(d[6] == 115 and d[7] == 0): #[+]
                    self.mode = 'local_angle'
                elif(d[6] == 165 and d[7] == 0): #[<]
                    self.mode = 'local'
                elif(d[6] == 163 and d[7] == 0): #[>]
                    self.toggle_constant_throttle()
                elif(d[6] == 114 and d[7] == 0): #[-]
                    self.mode = 'user'
                elif(d[6] == 164 and d[7] == 0): #[||]
                    '''
                    self.mode = 'user'
                    '''
                else:
                    bz = False

            elif (d[0] == 3):
                if(d[1] == 0):
                    self.lat3 = False
                elif(d[1] == 1):
                    self.lat3 = True
                elif(d[6] == 115 and d[7] == 0): #[+]
                    self.increase_max_throttle_10()
                elif(d[6] == 165 and d[7] == 0): #[<]
                    self.decrease_max_throttle_10()
                elif(d[6] == 163 and d[7] == 0): #[>]
                    self.inclease_ai_throttle_mult()
                elif(d[6] == 114 and d[7] == 0): #[-]
                    self.decrease_ai_throttle_mult()
                else:
                    bz = False

            else:
                bz = False

            if bz:
                GPIO.output(self.gpio_pin_buzzer, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(self.gpio_pin_buzzer, GPIO.LOW)
