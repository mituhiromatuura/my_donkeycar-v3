#!/usr/bin/env python3
"""
Scripts to drive a donkey 2 car

Usage:
    manage.py (drive) [--model=<model>] [--js] [--type=(linear|categorical|rnn|imu|behavior|3d|localizer|latent)] [--camera=(single|stereo)] [--meta=<key:value> ...] [--myconfig=<filename>]
    manage.py (train) [--tub=<tub1,tub2,..tubn>] [--file=<file> ...] (--model=<model>) [--transfer=<model>] [--type=(linear|categorical|rnn|imu|behavior|3d|localizer)] [--continuous] [--aug] [--myconfig=<filename>]


Options:
    -h --help               Show this screen.
    --js                    Use physical joystick.
    -f --file=<file>        A text file containing paths to tub files, one per line. Option may be used more than once.
    --meta=<key:value>      Key/Value strings describing describing a piece of meta data about this drive. Option may be used more than once.
    --myconfig=filename     Specify myconfig file to use. 
                            [default: myconfig.py]
"""
import os
import time

from docopt import docopt
import numpy as np

import donkeycar as dk

#import parts
from donkeycar.parts.transform import Lambda, TriggeredCallback, DelayedTrigger
from donkeycar.parts.datastore import TubHandler
from donkeycar.parts.controller import LocalWebController, \
    JoystickController, WebFpv
from donkeycar.parts.throttle_filter import ThrottleFilter
from donkeycar.parts.behavior import BehaviorPart
from donkeycar.parts.file_watcher import FileWatcher
from donkeycar.parts.launch import AiLaunch
from donkeycar.utils import *

import queue
q_button = queue.Queue()
q_rfcomm = queue.Queue()

def drive(cfg, model_path=None, use_joystick=False, model_type=None, camera_type='single', meta=[]):
    '''
    Construct a working robotic vehicle from many parts.
    Each part runs as a job in the Vehicle loop, calling either
    it's run or run_threaded method depending on the constructor flag `threaded`.
    All parts are updated one after another at the framerate given in
    cfg.DRIVE_LOOP_HZ assuming each part finishes processing in a timely manner.
    Parts may have named outputs and inputs. The framework handles passing named outputs
    to parts requesting the same named input.
    '''

    if cfg.DONKEY_GYM:
        #the simulator will use cuda and then we usually run out of resources
        #if we also try to use cuda. so disable for donkey_gym.
        os.environ["CUDA_VISIBLE_DEVICES"]="-1"

    if model_type is None:
        if cfg.TRAIN_LOCALIZER:
            model_type = "localizer"
        elif cfg.TRAIN_BEHAVIORS:
            model_type = "behavior"
        else:
            model_type = cfg.DEFAULT_MODEL_TYPE

    #Initialize car
    V = dk.vehicle.Vehicle()

    if cfg.USE_RFCOMM:
        from donkeycar.parts.rfcomm import RfComm
        V.add(RfComm(cfg, q_rfcomm, q_button), threaded=True)

    from donkeycar.parts.period_time import PeriodTime
    V.add(PeriodTime(cfg), inputs=['user/mode'], outputs=['period_time'])

    print("cfg.CAMERA_TYPE", cfg.CAMERA_TYPE)
    if camera_type == "stereo":

        if cfg.CAMERA_TYPE == "WEBCAM":
            from donkeycar.parts.camera import Webcam

            camA = Webcam(image_w=cfg.IMAGE_W, image_h=cfg.IMAGE_H, image_d=cfg.IMAGE_DEPTH, iCam = 0)
            camB = Webcam(image_w=cfg.IMAGE_W, image_h=cfg.IMAGE_H, image_d=cfg.IMAGE_DEPTH, iCam = 1)

        elif cfg.CAMERA_TYPE == "CVCAM":
            from donkeycar.parts.cv import CvCam

            camA = CvCam(image_w=cfg.IMAGE_W, image_h=cfg.IMAGE_H, image_d=cfg.IMAGE_DEPTH, iCam = 0)
            camB = CvCam(image_w=cfg.IMAGE_W, image_h=cfg.IMAGE_H, image_d=cfg.IMAGE_DEPTH, iCam = 1)
        else:
            raise(Exception("Unsupported camera type: %s" % cfg.CAMERA_TYPE))

        V.add(camA, outputs=['cam/image_array_a'], threaded=True)
        V.add(camB, outputs=['cam/image_array_b'], threaded=True)

        from donkeycar.parts.image import StereoPair

        V.add(StereoPair(), inputs=['cam/image_array_a', 'cam/image_array_b'],
            outputs=['cam/image_array'])
    elif cfg.CAMERA_TYPE == "D435":
        from donkeycar.parts.realsense435i import RealSense435i
        cam = RealSense435i(
            enable_rgb=cfg.REALSENSE_D435_RGB,
            enable_depth=cfg.REALSENSE_D435_DEPTH,
            enable_imu=cfg.REALSENSE_D435_IMU,
            device_id=cfg.REALSENSE_D435_ID)
        V.add(cam, inputs=[],
              outputs=['cam/image_array', 'cam/depth_array',
                       'imu/acl_x', 'imu/acl_y', 'imu/acl_z',
                       'imu/gyr_x', 'imu/gyr_y', 'imu/gyr_z'],
              threaded=True)

    else:
        if cfg.DONKEY_GYM:
            from donkeycar.parts.dgym import DonkeyGymEnv

        inputs = []
        threaded = True
        if cfg.DONKEY_GYM:
            from donkeycar.parts.dgym import DonkeyGymEnv 
            cam = DonkeyGymEnv(cfg.DONKEY_SIM_PATH, host=cfg.SIM_HOST, env_name=cfg.DONKEY_GYM_ENV_NAME, conf=cfg.GYM_CONF, delay=cfg.SIM_ARTIFICIAL_LATENCY)
            threaded = True
            inputs = ['angle', 'throttle']
        elif cfg.CAMERA_TYPE == "PICAM":
            from donkeycar.parts.camera import PiCamera
            cam = PiCamera(image_w=cfg.IMAGE_W, image_h=cfg.IMAGE_H, image_d=cfg.IMAGE_DEPTH, framerate=cfg.CAMERA_FRAMERATE, vflip=cfg.CAMERA_VFLIP, hflip=cfg.CAMERA_HFLIP)
        elif cfg.CAMERA_TYPE == "WEBCAM":
            from donkeycar.parts.camera import Webcam
            cam = Webcam(image_w=cfg.IMAGE_W, image_h=cfg.IMAGE_H, image_d=cfg.IMAGE_DEPTH)
        elif cfg.CAMERA_TYPE == "CVCAM":
            from donkeycar.parts.cv import CvCam
            cam = CvCam(image_w=cfg.IMAGE_W, image_h=cfg.IMAGE_H, image_d=cfg.IMAGE_DEPTH)
        elif cfg.CAMERA_TYPE == "CSIC":
            from donkeycar.parts.camera import CSICamera
            cam = CSICamera(image_w=cfg.IMAGE_W, image_h=cfg.IMAGE_H, image_d=cfg.IMAGE_DEPTH, framerate=cfg.CAMERA_FRAMERATE, gstreamer_flip=cfg.CSIC_CAM_GSTREAMER_FLIP_PARM)
        elif cfg.CAMERA_TYPE == "V4L":
            from donkeycar.parts.camera import V4LCamera
            cam = V4LCamera(image_w=cfg.IMAGE_W, image_h=cfg.IMAGE_H, image_d=cfg.IMAGE_DEPTH, framerate=cfg.CAMERA_FRAMERATE)
        elif cfg.CAMERA_TYPE == "MOCK":
            from donkeycar.parts.camera import MockCamera
            cam = MockCamera(image_w=cfg.IMAGE_W, image_h=cfg.IMAGE_H, image_d=cfg.IMAGE_DEPTH)
        elif cfg.CAMERA_TYPE == "IMAGE_LIST":
            from donkeycar.parts.camera import ImageListCamera
            cam = ImageListCamera(path_mask=cfg.PATH_MASK)
        else:
            raise(Exception("Unkown camera type: %s" % cfg.CAMERA_TYPE))

        V.add(cam, inputs=inputs, outputs=['cam/image_array_raw'], threaded=threaded)

    if (use_joystick or cfg.USE_JOYSTICK_AS_DEFAULT) and cfg.CONTROLLER_TYPE == "TTU":
        from donkeycar.parts.controller_propo import TTUJoystickController
        ctr = TTUJoystickController(
            q_button,
            q_rfcomm,
            throttle_dir=cfg.JOYSTICK_THROTTLE_DIR,
            throttle_scale=cfg.JOYSTICK_MAX_THROTTLE,
            steering_scale=cfg.JOYSTICK_STEERING_SCALE,
            auto_record_on_throttle=cfg.AUTO_RECORD_ON_THROTTLE)
        V.add(ctr,
            inputs=['cam/image_array_raw'],
            outputs =['user/angle_x', 'user/throttle_x', 'user/mode', 'recording',
                'ch1_x', 'ch2_x', 'ch3_x', 'ch4_x',
                'auto_record_on_throttle',
                'constant_throttle',
                'throttle_scale_x',
                'ai_throttle_mult_x',
                'auto_throttle_off',
                'disp_on',
                'esc_on',
                'VTXPower_value'
                ],
            threaded=True)

        if cfg.USE_SBUS:
            from donkeycar.parts.psoc_sbus import PsocCounter
            ctr = PsocCounter(cfg, '/dev/hidPsoc', q_button)
            V.add(ctr, outputs = ['user/angle', 'user/throttle', 'rpm', 'ch0', 
                                  'ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8', 
                                  'ch9', 'ch10', 'ch11', 'ch12',
                                  'ch13', 'ch14', 'ch15', 'ch16'], threaded=True)

            class SBus2Percent:
                def __init__(self, offset, x):
                    self.offset = offset
                    self.x = x

                def run(self, sbus):
                    return round((self.offset + sbus) * self.x, 2)

            V.add(SBus2Percent(  0, cfg.KMPH), inputs=['rpm'], outputs=['kmph'])
            V.add(SBus2Percent(100, 0.01), inputs=['ch3'], outputs=['throttle_scale'])
            V.add(SBus2Percent(100, 0.01), inputs=['ch4'], outputs=['ai_throttle_mult'])
            V.add(SBus2Percent(100, 1   ), inputs=['ch5'], outputs=['stop_range'])
            V.add(SBus2Percent(  0, 1   ), inputs=['ch6'], outputs=['gyro_gain'])
        else:
            from donkeycar.parts.psoc_counter import PsocCounter
            ctr = PsocCounter('/dev/hidPsoc')
            V.add(ctr, outputs = ['user/angle', 'user/throttle', 'ch4', 'ch1', 'ch2', 'ch3'], threaded=True)

    elif use_joystick or cfg.USE_JOYSTICK_AS_DEFAULT:
        #modify max_throttle closer to 1.0 to have more power
        #modify steering_scale lower than 1.0 to have less responsive steering
        if cfg.CONTROLLER_TYPE == "MM1":
            from donkeycar.parts.robohat import RoboHATController            
            ctr = RoboHATController(cfg)
        elif "custom" == cfg.CONTROLLER_TYPE:
            #
            # custom controller created with `donkey createjs` command
            #
            from my_joystick import MyJoystickController
            ctr = MyJoystickController(
                throttle_dir=cfg.JOYSTICK_THROTTLE_DIR,
                throttle_scale=cfg.JOYSTICK_MAX_THROTTLE,
                steering_scale=cfg.JOYSTICK_STEERING_SCALE,
                auto_record_on_throttle=cfg.AUTO_RECORD_ON_THROTTLE)
            ctr.set_deadzone(cfg.JOYSTICK_DEADZONE)
        else:
            from donkeycar.parts.controller import get_js_controller

            ctr = get_js_controller(cfg)

            if cfg.USE_NETWORKED_JS:
                from donkeycar.parts.controller import JoyStickSub
                netwkJs = JoyStickSub(cfg.NETWORK_JS_SERVER_IP)
                V.add(netwkJs, threaded=True)
                ctr.js = netwkJs
        
        V.add(ctr, 
          inputs=['cam/image_array'],
          outputs=['user/angle', 'user/throttle', 'user/mode', 'recording'],
          threaded=True)

    else:
        #This web controller will create a web server that is capable
        #of managing steering, throttle, and modes, and more.
        ctr = LocalWebController(port=cfg.WEB_CONTROL_PORT, mode=cfg.WEB_INIT_MODE)
        
        V.add(ctr,
          inputs=['cam/image_array', 'tub/num_records'],
          outputs=['user/angle', 'user/throttle', 'user/mode', 'recording'],
          threaded=True)

    #this throttle filter will allow one tap back for esc reverse
    th_filter = ThrottleFilter()
    #V.add(th_filter, inputs=['user/throttle'], outputs=['user/throttle'])

    #See if we should even run the pilot module.
    #This is only needed because the part run_condition only accepts boolean
    class PilotCondition:
        def run(self, mode):
            if mode == 'user':
                return False
            else:
                return True

    V.add(PilotCondition(), inputs=['user/mode'], outputs=['run_pilot'])

    class LedConditionLogic:
        def __init__(self, cfg):
            self.cfg = cfg

        def run(self, mode, recording, recording_alert, behavior_state, model_file_changed, track_loc):
            #returns a blink rate. 0 for off. -1 for on. positive for rate.

            if track_loc is not None:
                led.set_rgb(*self.cfg.LOC_COLORS[track_loc])
                return -1

            if model_file_changed:
                led.set_rgb(self.cfg.MODEL_RELOADED_LED_R, self.cfg.MODEL_RELOADED_LED_G, self.cfg.MODEL_RELOADED_LED_B)
                return 0.1
            else:
                led.set_rgb(self.cfg.LED_R, self.cfg.LED_G, self.cfg.LED_B)

            if recording_alert:
                led.set_rgb(*recording_alert)
                return self.cfg.REC_COUNT_ALERT_BLINK_RATE
            else:
                led.set_rgb(self.cfg.LED_R, self.cfg.LED_G, self.cfg.LED_B)

            if behavior_state is not None and model_type == 'behavior':
                r, g, b = self.cfg.BEHAVIOR_LED_COLORS[behavior_state]
                led.set_rgb(r, g, b)
                return -1 #solid on

            if recording:
                return -1 #solid on
            elif mode == 'user':
                return 1
            elif mode == 'local_angle':
                return 0.5
            elif mode == 'local':
                return 0.1
            return 0

    if cfg.HAVE_RGB_LED and not cfg.DONKEY_GYM:
        from donkeycar.parts.led_status import RGB_LED
        led = RGB_LED(cfg.LED_PIN_R, cfg.LED_PIN_G, cfg.LED_PIN_B, cfg.LED_INVERT)
        led.set_rgb(cfg.LED_R, cfg.LED_G, cfg.LED_B)

        V.add(LedConditionLogic(cfg), inputs=['user/mode', 'recording', "records/alert", 'behavior/state', 'modelfile/modified', "pilot/loc"],
              outputs=['led/blink_rate'])

        V.add(led, inputs=['led/blink_rate'])

    def get_record_alert_color(num_records):
        col = (0, 0, 0)
        for count, color in cfg.RECORD_ALERT_COLOR_ARR:
            if num_records >= count:
                col = color
        return col

    class RecordTracker:
        def __init__(self):
            self.last_num_rec_print = 0
            self.dur_alert = 0
            self.force_alert = 0

        def run(self, num_records):
            if num_records is None:
                return 0

            if self.last_num_rec_print != num_records or self.force_alert:
                self.last_num_rec_print = num_records

                if num_records % 10 == 0:
                    print("recorded", num_records, "records")

                if num_records % cfg.REC_COUNT_ALERT == 0 or self.force_alert:
                    self.dur_alert = num_records // cfg.REC_COUNT_ALERT * cfg.REC_COUNT_ALERT_CYC
                    self.force_alert = 0

            if self.dur_alert > 0:
                self.dur_alert -= 1

            if self.dur_alert != 0:
                return get_record_alert_color(num_records)

            return 0

    rec_tracker_part = RecordTracker()
    #V.add(rec_tracker_part, inputs=["tub/num_records"], outputs=['records/alert'])

    if cfg.AUTO_RECORD_ON_THROTTLE and isinstance(ctr, JoystickController):
        #then we are not using the circle button. hijack that to force a record count indication
        def show_record_acount_status():
            rec_tracker_part.last_num_rec_print = 0
            rec_tracker_part.force_alert = 1
        ctr.set_button_down_trigger('circle', show_record_acount_status)

    #Sombrero
    if cfg.HAVE_SOMBRERO:
        from donkeycar.parts.sombrero import Sombrero
        s = Sombrero()

    #IMU
    if cfg.HAVE_IMU:
        from donkeycar.parts.imu import IMU
        imu = IMU(sensor=cfg.IMU_SENSOR, dlp_setting=cfg.IMU_DLP_CONFIG)
        V.add(imu, outputs=['imu/acl_x', 'imu/acl_y', 'imu/acl_z',
            'imu/gyr_x', 'imu/gyr_y', 'imu/gyr_z'], threaded=True)

    #AHRS
    if cfg.HAVE_AHRS:
        '''
        from donkeycar.parts.mpu9250 import Mpu9250
        V.add(Mpu9250('/dev/ttyMPU9250'), outputs=[
            'imu/acl_x', 'imu/acl_y', 'imu/acl_z',
            'imu/gyr_x', 'imu/gyr_y', 'imu/gyr_z',
            'imu/mag_x', 'imu/mag_y', 'imu/mag_z',
            'imu/q_0', 'imu/q_x', 'imu/q_y', 'imu/q_z',
            'imu/ypr_y', 'imu/ypr_p', 'imu/ypr_r'],
            threaded=True)

        from donkeycar.parts.wt901c import Wt901c
        V.add(Wt901c('/dev/ttyWt901c'), outputs=[
            'imu/acl_x', 'imu/acl_y', 'imu/acl_z',
            'imu/gyr_x', 'imu/gyr_y', 'imu/gyr_z',
            'imu/mag_x', 'imu/mag_y', 'imu/mag_z',
            'imu/angle_x','imu/angle_y','imu/angle_z',
            'imu/q_0', 'imu/q_1', 'imu/q_2', 'imu/q_3'],
            threaded=True)
        '''
        from donkeycar.parts.wt901 import Wt901
        V.add(Wt901('/dev/ttyWt901'), outputs=[
            'imu/acl_x', 'imu/acl_y', 'imu/acl_z',
            'imu/gyr_x', 'imu/gyr_y', 'imu/gyr_z',
            'imu/mag_x', 'imu/mag_y', 'imu/mag_z',
            'imu/angle_x','imu/angle_y','imu/angle_z',
            'imu/q_0', 'imu/q_1', 'imu/q_2', 'imu/q_3'],
            threaded=True)

    #INA226
    if cfg.HAVE_INA226:
        from donkeycar.parts.ina226 import Ina226
        ina226_a = Ina226(0x48,(1000//30)/1000)
        V.add(ina226_a, outputs=['volt_a']) #, threaded=True)
        ina226_b = Ina226(0x49,(1000//30)/1000)
        V.add(ina226_b, outputs=['volt_b']) #, threaded=True)

    #ADS1115
    if cfg.HAVE_ADS1115:
        from donkeycar.parts.ads1115 import Ads1115
        V.add(Ads1115(0x4b), outputs=['dist0','dist1','dist2','dist3']) #, threaded=True)

    #PsocAdc
    if cfg.HAVE_PSOC_ADC:
        from donkeycar.parts.psoc_adc import PsocAdc
        V.add(PsocAdc('/dev/ttyPsoc'), outputs=['dist0','dist1','dist2','dist3','dist4','dist5','dist6','dist7'], threaded=True)

    #Vl53l0x
    if cfg.HAVE_VL53L0X:
        from donkeycar.parts.vl53l0x import Vl53l0x
        V.add(Vl53l0x('/dev/ttyVl53'), outputs=['dist0','dist4'], threaded=True)

    import cv2
    class ImageDist:
        def run(self, img, dist5, dist6):
            '''
            width = 160
            height = 120
            cv2.line(img,(0,height//4*3),(80-int(dist5*80/1200),height//4*3),(0,0,0),6)
            cv2.line(img,(0,height//4*3),(80-int(dist5*80/1200),height//4*3),(255,255,255),4)
            cv2.line(img,(width-1,height//4*3),(80+int(dist6*80/1200),height//4*3),(0,0,0),6)
            cv2.line(img,(width-1,height//4*3),(80+int(dist6*80/1200),height//4*3),(255,255,255),4)
            '''
            return img

    V.add(ImageDist(), inputs=['cam/image_array_raw', 'dist5', 'dist6'], outputs=['cam/image_array'])

    #LAMP
    if cfg.HAVE_LEDLAMP:
        from donkeycar.parts.lamp import LedCtrl
        V.add(LedCtrl(cfg), inputs = ['user/mode', 'user/throttle', 'auto_record_on_throttle', 'constant_throttle', 'esc_on'],
            outputs = ['led/head', 'led/tail', 'led/left', 'led/right', 'led/blue', 'led/green'])

        from donkeycar.parts.led_pca9685 import LED
        V.add(LED(), inputs=[
            'led/head',
            'led/left',
            'led/tail', #red in
            'led/left',
            'led/right',
            'led/tail', #red in
            'led/right',
            'led/head',

            'led/green', #green
            'led/head', #red out
            'led/left', #yerrow
            'led/blue', #blue

            'led/blue', #blue
            'led/right', #yerrow
            'led/head', #red out
            'led/green'], #green
            threaded=False) #True)

    class ImgPreProcess():
        '''
        preprocess camera image for inference.
        normalize and crop if needed.
        '''
        def __init__(self, cfg):
            self.cfg = cfg

        def run(self, img_arr):
            return normalize_and_crop(img_arr, self.cfg)

    if "coral" in model_type:
        inf_input = 'cam/image_array'
    else:
        inf_input = 'cam/normalized/cropped'
        V.add(ImgPreProcess(cfg),
            inputs=['cam/image_array'],
            outputs=[inf_input],
            run_condition='run_pilot')

    # Use the FPV preview, which will show the cropped image output, or the full frame.
    if cfg.USE_FPV:
        V.add(WebFpv(), inputs=['cam/image_array'], threaded=True)

    #Behavioral state
    if cfg.TRAIN_BEHAVIORS:
        bh = BehaviorPart(cfg.BEHAVIOR_LIST)
        V.add(bh, outputs=['behavior/state', 'behavior/label', "behavior/one_hot_state_array"])
        try:
            ctr.set_button_down_trigger('L1', bh.increment_state)
        except:
            pass

        inputs = [inf_input, "behavior/one_hot_state_array"]
    #IMU
    elif model_type == "imu":
        assert(cfg.HAVE_IMU)
        #Run the pilot if the mode is not user.
        inputs=[inf_input,
            'imu/acl_x', 'imu/acl_y', 'imu/acl_z',
            'imu/gyr_x', 'imu/gyr_y', 'imu/gyr_z']
    else:
        inputs=[inf_input]

    def load_model(kl, model_path):
        start = time.time()
        print('loading model', model_path)
        kl.load(model_path)
        print('finished loading in %s sec.' % (str(time.time() - start)) )

    def load_weights(kl, weights_path):
        start = time.time()
        try:
            print('loading model weights', weights_path)
            kl.model.load_weights(weights_path)
            print('finished loading in %s sec.' % (str(time.time() - start)) )
        except Exception as e:
            print(e)
            print('ERR>> problems loading weights', weights_path)

    def load_model_json(kl, json_fnm):
        start = time.time()
        print('loading model json', json_fnm)
        from tensorflow.python import keras
        try:
            with open(json_fnm, 'r') as handle:
                contents = handle.read()
                kl.model = keras.models.model_from_json(contents)
            print('finished loading json in %s sec.' % (str(time.time() - start)) )
        except Exception as e:
            print(e)
            print("ERR>> problems loading model json", json_fnm)

    if model_path:
        #When we have a model, first create an appropriate Keras part
        kl = dk.utils.get_model_by_type(model_type, cfg)

        model_reload_cb = None

        if '.h5' in model_path or '.uff' in model_path or 'tflite' in model_path or '.pkl' in model_path:
            #when we have a .h5 extension
            #load everything from the model file
            load_model(kl, model_path)

            def reload_model(filename):
                load_model(kl, filename)

            model_reload_cb = reload_model

        elif '.json' in model_path:
            #when we have a .json extension
            #load the model from there and look for a matching
            #.wts file with just weights
            load_model_json(kl, model_path)
            weights_path = model_path.replace('.json', '.weights')
            load_weights(kl, weights_path)

            def reload_weights(filename):
                weights_path = filename.replace('.json', '.weights')
                load_weights(kl, weights_path)

            model_reload_cb = reload_weights

        else:
            print("ERR>> Unknown extension type on model file!!")
            return

        '''
        #this part will signal visual LED, if connected
        V.add(FileWatcher(model_path, verbose=True), outputs=['modelfile/modified'])

        #these parts will reload the model file, but only when ai is running so we don't interrupt user driving
        V.add(FileWatcher(model_path), outputs=['modelfile/dirty'], run_condition="ai_running")
        V.add(DelayedTrigger(100), inputs=['modelfile/dirty'], outputs=['modelfile/reload'], run_condition="ai_running")
        V.add(TriggeredCallback(model_path, model_reload_cb), inputs=["modelfile/reload"], run_condition="ai_running")
        '''

        outputs=['pilot/angle', 'pilot/throttle']

        if cfg.TRAIN_LOCALIZER:
            outputs.append("pilot/loc")

        V.add(kl, inputs=inputs,
            outputs=outputs,
            run_condition='run_pilot')
    
    if cfg.STOP_SIGN_DETECTOR:
        from donkeycar.parts.object_detector.stop_sign_detector import StopSignDetector
        V.add(StopSignDetector(cfg.STOP_SIGN_MIN_SCORE, cfg.STOP_SIGN_SHOW_BOUNDING_BOX), inputs=['cam/image_array', 'pilot/throttle'], outputs=['pilot/throttle', 'cam/image_array'])

    #Choose what inputs should change the car.
    class DriveMode:

        def __init__(self):
            self.angle = 0.0

        def run(self, mode,
                    user_angle, user_throttle,
                    pilot_angle, pilot_throttle,
                    throttle_scale,
                    ai_throttle_mult,
                    stop_range,
                    ch8):

            if mode == 'user':
                user_throttle *= throttle_scale
                return user_angle, user_throttle

            elif mode == 'local_angle':
                pilot_angle = pilot_angle if pilot_angle else 0.0

                user_throttle *= throttle_scale
                return pilot_angle, user_throttle

            else:
                pilot_angle = pilot_angle if pilot_angle else 0.0
                pilot_throttle = pilot_throttle if pilot_throttle else 0.0

                '''
                if abs(self.angle - pilot_angle) < 0.3:
                    self.angle = pilot_angle
                else:
                    pilot_angle = self.angle
                '''

                if user_throttle > throttle_scale * 0.5:
                    return pilot_angle, -0.5

                if stop_range != 0:
                    if stop_range > ch8:
                        pilot_throttle = -0.5

                pilot_throttle *= throttle_scale * ai_throttle_mult
                return pilot_angle, pilot_throttle

    V.add(DriveMode(),
          inputs=['user/mode', 'user/angle', 'user/throttle',
                  'pilot/angle', 'pilot/throttle',
                  'throttle_scale',
                  'ai_throttle_mult',
                  'stop_range',
                  'ch8'],
          outputs=['angle', 'throttle'])


    class V2Esp32():

        def __init__(self, q_rfcomm):
            self.q_rfcomm = q_rfcomm
            self.esc_on = False
            self.recording = False
            self.mode = ""
            self.throttle_scale = 201
            self.ai_throttle_mult = 201
            self.gyro_gain = 201
            self.stop_range = 201

            self.q_rfcomm.put("ESC_"+ ("ON" if self.esc_on else "OFF") +" 80," + str(30*1) +",130,30,3\n")
            self.q_rfcomm.put("REC_"+ ("ON" if self.recording else "OFF") +" 80," + str(30*2) +",130,30,3\n")

            self.sec = time.time()

        def run(self, esc_on, recording, mode, throttle_scale, ai_throttle_mult, gyro_gain, stop_range, volt_a, volt_b):
            if self.mode != mode:
                self.mode = mode
                self.q_rfcomm.put(self.mode + " 0,0," + str(240-15) +",30,3\n")
            if self.throttle_scale != throttle_scale:
                self.throttle_scale = throttle_scale
                self.q_rfcomm.put(str(self.throttle_scale) + " 0," + str(30*1) +",80,30,3\n")
            if self.ai_throttle_mult != ai_throttle_mult:
                self.ai_throttle_mult = ai_throttle_mult
                self.q_rfcomm.put(str(self.ai_throttle_mult) + " 0," + str(30*2) +",80,30,3\n")
            if self.gyro_gain != gyro_gain:
                self.gyro_gain = gyro_gain
                self.q_rfcomm.put(str(self.gyro_gain) + " 0," + str(30*3) +",80,30,3\n")
            if self.stop_range != stop_range:
                self.stop_range = stop_range
                self.q_rfcomm.put(str(self.stop_range) + " 0," + str(30*4) +",80,30,3\n")
            if self.esc_on != esc_on:
                self.esc_on = esc_on
                self.q_rfcomm.put("ESC_"+ ("ON" if esc_on else "OFF") +" 80," + str(30*1) +",130,30,3\n")
            if self.recording != recording:
                self.recording = recording
                self.q_rfcomm.put("REC_"+ ("ON" if recording else "OFF") +" 80," + str(30*2) +",130,30,3\n")

            if time.time() - self.sec > 1:
                self.sec = time.time()
                self.q_rfcomm.put(str(round(volt_b,2)) + " 0," + str(30*6) +",80,30,3\n")
                self.q_rfcomm.put(str(round(volt_a,2)) + " 0," + str(30*7) +",80,30,3\n")


    if cfg.USE_RFCOMM:
        V.add(V2Esp32(q_rfcomm), inputs=['esc_on', 'recording', 'user/mode', 'throttle_scale', 'ai_throttle_mult', 'gyro_gain', 'stop_range', 'volt_a', 'volt_b'])


    '''
    #to give the car a boost when starting ai mode in a race.
    aiLauncher = AiLaunch(cfg.AI_LAUNCH_DURATION, cfg.AI_LAUNCH_THROTTLE, cfg.AI_LAUNCH_KEEP_ENABLED)

    V.add(aiLauncher,
        inputs=['user/mode', 'throttle'],
        outputs=['throttle'])

    if isinstance(ctr, JoystickController):
        ctr.set_button_down_trigger(cfg.AI_LAUNCH_ENABLE_BUTTON, aiLauncher.enable_ai_launch)
    '''


    class AiRunCondition:
        '''
        A bool part to let us know when ai is running.
        '''
        def run(self, mode):
            if mode == "user":
                return False
            return True

    V.add(AiRunCondition(), inputs=['user/mode'], outputs=['ai_running'])

    #Ai Recording
    class AiRecordingCondition:
        '''
        return True when ai mode, otherwize respect user mode recording flag
        '''
        def run(self, mode, recording):
            if mode == 'user':
                return recording
            return True

    if cfg.RECORD_DURING_AI:
        V.add(AiRecordingCondition(), inputs=['user/mode', 'recording'], outputs=['recording'])

    #Drive train setup
    if cfg.DONKEY_GYM or cfg.DRIVE_TRAIN_TYPE == "MOCK":
        pass
    elif cfg.DRIVE_TRAIN_TYPE == "SERVO_ESC":
        from donkeycar.parts.actuator import PCA9685, PWMSteering, PWMThrottle

        steering_controller = PCA9685(cfg.STEERING_CHANNEL, cfg.PCA9685_I2C_ADDR, busnum=cfg.PCA9685_I2C_BUSNUM)
        steering = PWMSteering(controller=steering_controller,
                                        left_pulse=cfg.STEERING_LEFT_PWM,
                                        right_pulse=cfg.STEERING_RIGHT_PWM)

        throttle_controller = PCA9685(cfg.THROTTLE_CHANNEL, cfg.PCA9685_I2C_ADDR, busnum=cfg.PCA9685_I2C_BUSNUM)
        throttle = PWMThrottle(controller=throttle_controller,
                                        max_pulse=cfg.THROTTLE_FORWARD_PWM,
                                        zero_pulse=cfg.THROTTLE_STOPPED_PWM,
                                        min_pulse=cfg.THROTTLE_REVERSE_PWM)

        V.add(steering, inputs=['angle'], threaded=True)
        V.add(throttle, inputs=['throttle'], threaded=True)


    elif cfg.DRIVE_TRAIN_TYPE == "DC_STEER_THROTTLE":
        from donkeycar.parts.actuator import Mini_HBridge_DC_Motor_PWM

        steering = Mini_HBridge_DC_Motor_PWM(cfg.HBRIDGE_PIN_LEFT, cfg.HBRIDGE_PIN_RIGHT)
        throttle = Mini_HBridge_DC_Motor_PWM(cfg.HBRIDGE_PIN_FWD, cfg.HBRIDGE_PIN_BWD)

        V.add(steering, inputs=['angle'])
        V.add(throttle, inputs=['throttle'])


    elif cfg.DRIVE_TRAIN_TYPE == "DC_TWO_WHEEL":
        from donkeycar.parts.actuator import TwoWheelSteeringThrottle, Mini_HBridge_DC_Motor_PWM

        left_motor = Mini_HBridge_DC_Motor_PWM(cfg.HBRIDGE_PIN_LEFT_FWD, cfg.HBRIDGE_PIN_LEFT_BWD)
        right_motor = Mini_HBridge_DC_Motor_PWM(cfg.HBRIDGE_PIN_RIGHT_FWD, cfg.HBRIDGE_PIN_RIGHT_BWD)
        two_wheel_control = TwoWheelSteeringThrottle()

        V.add(two_wheel_control,
                inputs=['throttle', 'angle'],
                outputs=['left_motor_speed', 'right_motor_speed'])

        V.add(left_motor, inputs=['left_motor_speed'])
        V.add(right_motor, inputs=['right_motor_speed'])

    elif cfg.DRIVE_TRAIN_TYPE == "SERVO_HBRIDGE_PWM":
        from donkeycar.parts.actuator import ServoBlaster, PWMSteering
        steering_controller = ServoBlaster(cfg.STEERING_CHANNEL) #really pin
        #PWM pulse values should be in the range of 100 to 200
        assert(cfg.STEERING_LEFT_PWM <= 200)
        assert(cfg.STEERING_RIGHT_PWM <= 200)
        steering = PWMSteering(controller=steering_controller,
                                        left_pulse=cfg.STEERING_LEFT_PWM,
                                        right_pulse=cfg.STEERING_RIGHT_PWM)


        from donkeycar.parts.actuator import Mini_HBridge_DC_Motor_PWM
        motor = Mini_HBridge_DC_Motor_PWM(cfg.HBRIDGE_PIN_FWD, cfg.HBRIDGE_PIN_BWD)

        V.add(steering, inputs=['angle'], threaded=True)
        V.add(motor, inputs=["throttle"])
        
    elif cfg.DRIVE_TRAIN_TYPE == "MM1":
        from donkeycar.parts.robohat import RoboHATDriver
        V.add(RoboHATDriver(cfg), inputs=['angle', 'throttle'])
    
    elif cfg.DRIVE_TRAIN_TYPE == "PIGPIO_PWM":
        from donkeycar.parts.actuator_pigpio import PWMSteering, PWMThrottle, PiGPIO_PWM, PiGPIO_SWPWM
        steering_controller = PiGPIO_PWM(cfg.STEERING_PWM_PIN, freq=cfg.STEERING_PWM_FREQ, inverted=cfg.STEERING_PWM_INVERTED,
                                         center=cfg.STEERING_CENTER_PWM)
        steering = PWMSteering(controller=steering_controller,
                                        left_pulse=cfg.STEERING_LEFT_PWM, 
                                        right_pulse=cfg.STEERING_RIGHT_PWM)
        
        throttle_controller = PiGPIO_PWM(cfg.THROTTLE_PWM_PIN, freq=cfg.THROTTLE_PWM_FREQ, inverted=cfg.THROTTLE_PWM_INVERTED,
                                         center=cfg.THROTTLE_STOPPED_PWM)
        throttle = PWMThrottle(controller=throttle_controller,
                                            max_pulse=cfg.THROTTLE_FORWARD_PWM,
                                            zero_pulse=cfg.THROTTLE_STOPPED_PWM, 
                                            min_pulse=cfg.THROTTLE_REVERSE_PWM)
        V.add(steering, inputs=['angle', 'ch9', 'ch11'])
        V.add(throttle, inputs=['throttle', 'ch10', 'ch12'])
    
        lidar_controller = PiGPIO_SWPWM(cfg.LIDAR_PWM_PIN, freq=cfg.LIDAR_PWM_FREQ, inverted=cfg.LIDAR_PWM_INVERTED,
                                      center=cfg.LIDAR_CENTER_PWM)
        lidar = PWMSteering(controller=lidar_controller,
                                        left_pulse=cfg.LIDAR_RIGHT_PWM, 
                                        right_pulse=cfg.LIDAR_LEFT_PWM)
        V.add(lidar, inputs=['angle', 'ch13', 'ch15'])

    elif cfg.DRIVE_TRAIN_TYPE == "PSOC_I2C_PWM":
        from donkeycar.parts.actuator_psoc import PsocI2cPwm
        psoc_i2c_pwm = PsocI2cPwm(cfg)
        V.add(psoc_i2c_pwm, inputs=['angle', 'throttle'])

    # OLED setup
    if cfg.USE_SSD1306_128_32:
        from donkeycar.parts.oled import OLEDPart
        auto_record_on_throttle = cfg.USE_JOYSTICK_AS_DEFAULT and cfg.AUTO_RECORD_ON_THROTTLE
        oled_part = OLEDPart(cfg.SSD1306_128_32_I2C_BUSNUM, auto_record_on_throttle=auto_record_on_throttle)
        V.add(oled_part, inputs=['recording', 'tub/num_records', 'user/mode'], outputs=[], threaded=True)

    #add tub to save data

    inputs=['cam/image_array',
            'user/angle', 'user/throttle',
            'user/mode']

    types=['image_array',
           'float', 'float',
           'str']

    if cfg.TRAIN_BEHAVIORS:
        inputs += ['behavior/state', 'behavior/label', "behavior/one_hot_state_array"]
        types += ['int', 'str', 'vector']

    if cfg.CAMERA_TYPE == "D435" and cfg.REALSENSE_D435_DEPTH:
        inputs += ['cam/depth_array']
        types += ['gray16_array']

    if cfg.HAVE_IMU or (cfg.CAMERA_TYPE == "D435" and cfg.REALSENSE_D435_IMU):
        inputs += ['imu/acl_x', 'imu/acl_y', 'imu/acl_z',
            'imu/gyr_x', 'imu/gyr_y', 'imu/gyr_z']

        types +=['float', 'float', 'float',
           'float', 'float', 'float']

    if cfg.RECORD_DURING_AI:
        inputs += ['pilot/angle', 'pilot/throttle']
        types += ['float', 'float']

    th = TubHandler(path=cfg.DATA_PATH)
    tub = th.new_tub_writer(inputs=inputs, types=types, user_meta=meta)
    V.add(tub, inputs=inputs, outputs=["tub/num_records"], run_condition='recording')

    if cfg.PUB_CAMERA_IMAGES:
        from donkeycar.parts.network import TCPServeValue
        from donkeycar.parts.image import ImgArrToJpg
        pub = TCPServeValue("camera")
        V.add(ImgArrToJpg(), inputs=['cam/image_array'], outputs=['jpg/bin'])
        V.add(pub, inputs=['jpg/bin'])

    if type(ctr) is LocalWebController:
        if cfg.DONKEY_GYM:
            print("You can now go to http://localhost:%d to drive your car." % cfg.WEB_CONTROL_PORT)
        else:
            print("You can now go to <your hostname.local>:%d to drive your car." % cfg.WEB_CONTROL_PORT)
    elif isinstance(ctr, JoystickController):
        print("You can now move your joystick to drive your car.")
        #tell the controller about the tub
        ctr.set_tub(tub)

        if cfg.BUTTON_PRESS_NEW_TUB:

            def new_tub_dir():
                V.parts.pop()
                tub = th.new_tub_writer(inputs=inputs, types=types, user_meta=meta)
                V.add(tub, inputs=inputs, outputs=["tub/num_records"], run_condition='recording')
                ctr.set_tub(tub)

            ctr.set_button_down_trigger('cross', new_tub_dir)
        ctr.print_controls()

    if cfg.USE_FPVDISP:
        from donkeycar.parts.fpvdisp import FPVDisp
        V.add(FPVDisp(cfg, q_button),
            inputs=[
                'user/mode',
                'cam/image_array_raw',
                'angle',
                'throttle',
                'lap',
                'kmph',
                'rpm',
                'ch0',
                'ch1',
                'ch2',
                'ch3',
                'ch4',
                'ch5',
                'ch6',
                'ch7',
                'ch8',
                'imu/acl_x',
                'imu/acl_y',
                'imu/acl_z',
                'imu/gyr_x',
                'imu/gyr_y',
                'imu/gyr_z',
                'imu/mag_x',
                'imu/mag_y',
                'imu/mag_z',
                'imu/angle_x',
                'imu/angle_y',
                'imu/angle_z',
                'imu/q_0',
                'imu/q_1',
                'imu/q_2',
                'imu/q_3',
                'volt_a',
                'volt_b',
                'recording',
                'auto_record_on_throttle',
                'constant_throttle',
                'throttle_scale',
                'ai_throttle_mult',
                'gyro_gain',
                'stop_range',
                'disp_on',
                'esc_on',
                'tub/num_records',
                'period_time'
            ],
            threaded=False #True
        )

    if cfg.HAVE_BUZZER:
        from donkeycar.parts.buzzer import Buzzer
        V.add(Buzzer(cfg, q_rfcomm), inputs=['esc_on', 'tub/num_records', 'period_time', 'imu/gyr_z'], outputs=['lap'])

    if True:
        from donkeycar.parts.log import Log
        V.add(Log(cfg),
            inputs=[
                'tub/num_records',
                'period_time',
                'volt_a',
                'volt_b',
                'angle',
                'throttle',
                'user/angle',
                'user/throttle',
                'user/mode',
                'pilot/angle',
                'pilot/throttle',
                'lap',
                'kmph',
                'rpm',
                'ch0',
                'ch1',
                'ch2',
                'ch3',
                'ch4',
                'ch5',
                'ch6',
                'ch7',
                'ch8',
                'ch9',
                'ch10',
                'ch11',
                'ch12',
                'ch13',
                'ch14',
                'ch15',
                'ch16',
                'imu/acl_x',
                'imu/acl_y',
                'imu/acl_z',
                'imu/gyr_x',
                'imu/gyr_y',
                'imu/gyr_z',
                'imu/mag_x',
                'imu/mag_y',
                'imu/mag_z',
                'imu/angle_x',
                'imu/angle_y',
                'imu/angle_z',
                'imu/q_0',
                'imu/q_1',
                'imu/q_2',
                'imu/q_3',
                'throttle_scale',
                'ai_throttle_mult',
                'gyro_gain',
                'stop_range',
            ])

    #run the vehicle for 20 seconds
    V.start(rate_hz=1000, #cfg.DRIVE_LOOP_HZ,
            max_loop_count=cfg.MAX_LOOPS)


if __name__ == '__main__':
    args = docopt(__doc__)
    cfg = dk.load_config(myconfig=args['--myconfig'])

    if args['drive']:
        model_type = args['--type']
        camera_type = args['--camera']

        drive(cfg, model_path=args['--model'], use_joystick=args['--js'],
              model_type=model_type, camera_type=camera_type,
              meta=args['--meta'])

    if args['train']:
        from train import multi_train, preprocessFileList

        tub = args['--tub']
        model = args['--model']
        transfer = args['--transfer']
        model_type = args['--type']
        continuous = args['--continuous']
        aug = args['--aug']
        dirs = preprocessFileList( args['--file'] )

        if tub is not None:
            tub_paths = [os.path.expanduser(n) for n in tub.split(',')]
            dirs.extend( tub_paths )

        if model_type is None:
            model_type = cfg.DEFAULT_MODEL_TYPE
            print("using default model type of", model_type)

        multi_train(cfg, dirs, model, transfer, model_type, continuous, aug)

