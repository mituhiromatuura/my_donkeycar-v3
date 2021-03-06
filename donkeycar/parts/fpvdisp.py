import os
import time
import numpy as np
import cv2
import concurrent.futures
import queue
import RPi.GPIO as GPIO

class FPVDisp:
    def __init__(self, cfg, q_button):
        self.cfg = cfg
        self.q_button = q_button
        self.time = time.time()
        self.rectime = time.time()
        self.executor_on = False

        self.led_off = GPIO.HIGH
        self.led_on = GPIO.LOW

        GPIO.setmode(GPIO.BOARD)

        self.gpio_pin_rec = 31 #GPIO6
        GPIO.setup(self.gpio_pin_rec, GPIO.OUT)
        GPIO.output(self.gpio_pin_rec, self.led_off)

        self.gpio_pin_const = 22 #GPIO25 26 #GPIO7
        GPIO.setup(self.gpio_pin_const, GPIO.OUT)
        GPIO.output(self.gpio_pin_const, self.led_off)

        self.gpio_pin_local_angle = 18 #GPIO24 24 #GPIO8
        GPIO.setup(self.gpio_pin_local_angle, GPIO.OUT)
        GPIO.output(self.gpio_pin_local_angle, self.led_off)

        self.gpio_pin_local = 15 #GPIO22 23 #GPIO11
        GPIO.setup(self.gpio_pin_local, GPIO.OUT)
        GPIO.output(self.gpio_pin_local, self.led_off)

        self.gpio_pin_vtb_on = 11 #GPIO17
        GPIO.setup(self.gpio_pin_vtb_on, GPIO.OUT)
        if self.cfg.VTB_ON:
            GPIO.output(self.gpio_pin_vtb_on, GPIO.HIGH)
        else:
            GPIO.output(self.gpio_pin_vtb_on, GPIO.LOW)

        self.gpio_pin_buzzer = 36 #GPIO20
        GPIO.setup(self.gpio_pin_buzzer, GPIO.OUT)
        GPIO.output(self.gpio_pin_buzzer, GPIO.LOW)

        GPIO.output(self.gpio_pin_buzzer, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(self.gpio_pin_buzzer, GPIO.LOW)

        self.fullscreen = True
        self.disp_imu = True
        self.disp_callsign = self.cfg.VTB_ON
        self.on = True
        '''
        self.executor = concurrent.futures.ProcessPoolExecutor(max_workers=1)
        '''

    '''
    def run_threaded(self,
        mode,
        image,
        angle,
        throttle,
        lap,
        kmph,
        rpm,
        ch0,
        ch1,
        ch2,
        ch3,
        ch4,
        ch5,
        ch6,
        ch7,
        ch8,
        imu_acl_x,
        imu_acl_y,
        imu_acl_z,
        imu_gyr_x,
        imu_gyr_y,
        imu_gyr_z,
        imu_mag_x,
        imu_mag_y,
        imu_mag_z,
        imu_angle_x,
        imu_angle_y,
        imu_angle_z,
        imu_q_0,
        imu_q_1,
        imu_q_2,
        imu_q_3,
        volt_a,
        volt_b,
        recording,
        auto_record_on_throttle,
        constant_throttle,
        throttle_scale,
        ai_throttle_mult,
        gyro_gain,
        stop_range,
        disp_on,
        esc_on,
        num_records,
        period_time):

        self.executor_on = True

        self.mode = mode
        self.image = image
        self.angle = angle
        self.throttle = throttle
        self.lap = lap,
        self.kmph = kmph,
        self.rpm = rpm,
        self.ch0 = ch0,
        self.ch1 = ch1,
        self.ch2 = ch2,
        self.ch3 = ch3,
        self.ch4 = ch4,
        self.ch5 = ch5,
        self.ch6 = ch6,
        self.ch7 = ch7,
        self.ch8 = ch8,
        self.imu_acl_x = imu_acl_x
        self.imu_acl_y = imu_acl_y
        self.imu_acl_z = imu_acl_z
        self.imu_gyr_x = imu_gyr_x
        self.imu_gyr_y = imu_gyr_y
        self.imu_gyr_z = imu_gyr_z
        self.imu_mag_x = imu_mag_x
        self.imu_mag_y = imu_mag_y
        self.imu_mag_z = imu_mag_z
        self.imu_angle_x = imu_angle_x
        self.imu_angle_y = imu_angle_y
        self.imu_angle_z = imu_angle_z
        self.imu_q_0 = imu_q_0
        self.imu_q_1 = imu_q_1
        self.imu_q_2 = imu_q_2
        self.imu_q_3 = imu_q_3
        self.volt_a = volt_a
        self.volt_b = volt_b
        self.recording = recording
        self.auto_record_on_throttle = auto_record_on_throttle
        self.constant_throttle = constant_throttle
        self.throttle_scale = throttle_scale
        self.ai_throttle_mult = ai_throttle_mult
        self,gyro_gain = gyro_gain
        self.stop_range = stop_range
        self.disp_on = disp_on
        self.esc_on = esc_on
        self.num_records = num_records
        self.period_time = period_time
    '''

    def run(self,
        mode,
        image,
        angle,
        throttle,
        lap,
        kmph,
        rpm,
        ch0,
        ch1,
        ch2,
        ch3,
        ch4,
        ch5,
        ch6,
        ch7,
        ch8,
        imu_acl_x,
        imu_acl_y,
        imu_acl_z,
        imu_gyr_x,
        imu_gyr_y,
        imu_gyr_z,
        imu_mag_x,
        imu_mag_y,
        imu_mag_z,
        imu_angle_x,
        imu_angle_y,
        imu_angle_z,
        imu_q_0,
        imu_q_1,
        imu_q_2,
        imu_q_3,
        volt_a,
        volt_b,
        recording,
        auto_record_on_throttle,
        constant_throttle,
        throttle_scale,
        ai_throttle_mult,
        gyro_gain,
        stop_range,
        disp_on,
        esc_on,
        num_records,
        period_time):

        if self.on:
            self.mode = mode
            self.image = image
            self.angle = angle
            self.throttle = throttle
            self.lap = lap
            self.kmph = kmph
            self.rpm = rpm
            self.ch0 = ch0
            self.ch1 = ch1
            self.ch2 = ch2
            self.ch3 = ch3
            self.ch4 = ch4
            self.ch5 = ch5
            self.ch6 = ch6
            self.ch7 = ch7
            self.ch8 = ch8
            self.imu_acl_x = imu_acl_x
            self.imu_acl_y = imu_acl_y
            self.imu_acl_z = imu_acl_z
            self.imu_gyr_x = imu_gyr_x
            self.imu_gyr_y = imu_gyr_y
            self.imu_gyr_z = imu_gyr_z
            self.imu_mag_x = imu_mag_x
            self.imu_mag_y = imu_mag_y
            self.imu_mag_z = imu_mag_z
            self.imu_angle_x = imu_angle_x
            self.imu_angle_y = imu_angle_y
            self.imu_angle_z = imu_angle_z
            self.imu_q_0 = imu_q_0
            self.imu_q_1 = imu_q_1
            self.imu_q_2 = imu_q_2
            self.imu_q_3 = imu_q_3
            self.volt_a = volt_a
            self.volt_b = volt_b
            self.recording = recording
            self.auto_record_on_throttle = auto_record_on_throttle
            self.constant_throttle = constant_throttle
            self.throttle_scale = throttle_scale
            self.ai_throttle_mult = ai_throttle_mult
            self.gyro_gain = gyro_gain
            self.stop_range = stop_range
            self.disp_on = disp_on
            self.esc_on = esc_on
            self.num_records = num_records
            self.period_time = period_time

            #self.executor.submit(self.disp_main())
            self.disp_main()

    '''
    def update(self):
        while self.on:
            if self.executor_on == True:
                self.executor.submit(self.disp_main())
                time.sleep((1/self.cfg.DRIVE_LOOP_HZ))
    '''

    def disp_main(self):
        try:
            if self.num_records % 1000 == 0:
                print(self.num_records)
        except:
            pass

        if self.constant_throttle:
            GPIO.output(self.gpio_pin_const, self.led_on)
        else:
            GPIO.output(self.gpio_pin_const, self.led_off)

        if self.auto_record_on_throttle:
            GPIO.output(self.gpio_pin_rec, self.led_on)
        else:
            GPIO.output(self.gpio_pin_rec, self.led_off)

        if self.mode == 'user':
            GPIO.output(self.gpio_pin_local_angle, self.led_off)
            GPIO.output(self.gpio_pin_local, self.led_off)
        else:
            if self.mode == 'local_angle':
                GPIO.output(self.gpio_pin_local_angle, self.led_on)
                GPIO.output(self.gpio_pin_local, self.led_off)
            elif self.mode == 'local':
                GPIO.output(self.gpio_pin_local_angle, self.led_on)
                GPIO.output(self.gpio_pin_local, self.led_on)

        if not self.disp_on:
            return

        cv2.namedWindow('DonkeyCamera', cv2.WINDOW_NORMAL)
        #cv2.namedWindow('DonkeyCamera', cv2.WINDOW_AUTOSIZE)

        if self.recording:
            color = (255,0,0) #red
        elif not self.esc_on:
            color = (255,255,0) #yellow
        else:
            color = (0,255,0) #green

        wwidth = self.cfg.IMAGE_W
        wheight = self.cfg.IMAGE_H

        '''
        width = self.cfg.IMAGE_W
        height = self.cfg.IMAGE_H

        if(width == wwidth):
            img1=self.image.copy()
            #cv2.flip(self.image, -1)
        else:
            flame = np.zeros((height, wwidth-width, 3), np.uint)
            img1 = cv2.hconcat([self.image.copy(), flame])
        if(height != wheight):
            flame = np.zeros((wheight-height, wwidth, 3), np.uint)
            img = cv2.vconcat([img1, flame])
        else:
            img = img2
        '''

        try:
            img = self.image.copy()
        except:
            return
        #img = cv2.vconcat([self.image.copy(), self.image.copy()])

        x0=int(round(wwidth/2))
        y0=int(round(wheight))
        x1=int(round(wwidth/2 + wwidth/2*self.angle * (1 if self.cfg.SBUS_CH1_MIN < self.cfg.SBUS_CH1_MAX else -1)))
        y1=int(round(wheight + wheight*self.throttle * (1 if self.cfg.SBUS_CH2_MIN < self.cfg.SBUS_CH2_MAX else -1)))

        cv2.line(img,(x0 ,y0),(x1,y1),color,2)

        textFontFace = cv2.FONT_HERSHEY_SIMPLEX
        #textFontFace = cv2.FONT_HERSHEY_PLAIN
        #textFontFace = cv2.FONT_HERSHEY_DUPLEX
        #textFontFace = cv2.FONT_HERSHEY_COMPLEX
        #textFontFace = cv2.FONT_HERSHEY_TRIPLEX
        #textFontFace = cv2.FONT_HERSHEY_COMPLEX_SMALL
        #textFontFace = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
        #textFontFace = cv2.FONT_HERSHEY_SCRIPT_COMPLEX

        textFontScale = 0.4
        textColor = (0,255,0)
        textThickness = 1

        cv2.putText(img,self.mode,(0,9),textFontFace,textFontScale,textColor,textThickness)
        if self.constant_throttle:
            cv2.putText(img,'CONST',(8*9,9),textFontFace,textFontScale,textColor,textThickness)
        if self.disp_callsign:
            cv2.putText(img,'JS2IHP',(wwidth-8*6,29),textFontFace,textFontScale,textColor,textThickness)
            GPIO.output(self.gpio_pin_vtb_on, GPIO.HIGH)
        else:
            GPIO.output(self.gpio_pin_vtb_on, GPIO.LOW)
        if self.auto_record_on_throttle:
            cv2.putText(img,'REC',(wwidth-8*3,19),textFontFace,textFontScale,(255,0,0),textThickness)

        cv2.putText(img,str(self.throttle_scale),(0,19),textFontFace,textFontScale,textColor,textThickness)
        cv2.putText(img,str(self.ai_throttle_mult),(0,29),textFontFace,textFontScale,textColor,textThickness)
        cv2.putText(img,str(self.gyro_gain),(0,39),textFontFace,textFontScale,textColor,textThickness)
        cv2.putText(img,str(self.stop_range),(0,49),textFontFace,textFontScale,textColor,textThickness)
        cv2.putText(img,str(self.ch8),(0,59),textFontFace,textFontScale,textColor,textThickness)

        if self.cfg.HAVE_VL53L0X:
            cv2.putText(img,str(self.dist_slow),(0,49),textFontFace,textFontScale,textColor,textThickness)
            cv2.putText(img,str(self.dist_stop),(0,59),textFontFace,textFontScale,textColor,textThickness)
            cv2.putText(img,str(self.dist_throttle_off),(0,69),textFontFace,textFontScale,textColor,textThickness)

        if self.esc_on == False:
            cv2.putText(img,'ESC OFF',(wwidth-8*7,9),textFontFace,textFontScale,textColor,textThickness)

        cv2.putText(img,str(self.lap),(0,wheight-31),textFontFace,textFontScale,textColor,textThickness)
        #cv2.putText(img,str(self.cfg.DRIVE_LOOP_HZ),(0,79),textFontFace,textFontScale,textColor,textThickness)
        if self.mode == "user" and not self.auto_record_on_throttle:
            self.rectime = time.time()
            sec = 0
        else:
            sec=int(time.time()-self.rectime)
        cv2.putText(img,str(sec//60)+':'+str(sec%60),(0,wheight-21),textFontFace,textFontScale,textColor,textThickness)
        cv2.putText(img,str(self.num_records),(90,wheight-21),textFontFace,textFontScale,textColor,textThickness)

        cv2.putText(img,str(self.ch1),(90,wheight-11),textFontFace,textFontScale,textColor,textThickness)
        cv2.putText(img,str(self.ch2),(127,wheight-11),textFontFace,textFontScale,textColor,textThickness)
        if self.cfg.HAVE_REVCOUNT:
            cv2.putText(img,str(self.rpm),(90,wheight-1),textFontFace,textFontScale,textColor,textThickness)
            cv2.putText(img,"{:.1f}".format(self.kmph),(40,wheight-1),textFontFace,textFontScale,textColor,textThickness)
        #cv2.putText(img,str(self.throttle),(100,wheight-31),textFontFace,textFontScale,textColor,textThickness)

        if self.cfg.HAVE_IMU:
            #if self.disp_imu:
            if self.sw_r3:
                self.imu_acl_x /= 1000
                self.imu_acl_y /= 1000
                self.imu_acl_z /= 1000
                self.imu_gyr_x /= 100
                self.imu_gyr_y /= 100
                self.imu_gyr_z /= 1

                '''
                cv2.putText(img,str(round(self.imu_acl_x,2)),(0,69),textFontFace,textFontScale,textColor,textThickness)
                cv2.putText(img,str(round(self.imu_acl_y,2)),(0,79),textFontFace,textFontScale,textColor,textThickness)
                cv2.putText(img,str(round(self.imu_acl_z,2)),(0,89),textFontFace,textFontScale,textColor,textThickness)
                cv2.putText(img,str(round(self.imu_gyr_x,2)),(0,99),textFontFace,textFontScale,textColor,textThickness)
                cv2.putText(img,str(round(self.imu_gyr_y,2)),(0,109),textFontFace,textFontScale,textColor,textThickness)
                cv2.putText(img,str(round(self.imu_gyr_z,2)),(0,119),textFontFace,textFontScale,textColor,textThickness)
                '''

                cv2.line(img,(wwidth//2,0),(wwidth//2,wheight-1),(255,255,0),1)
                cv2.line(img,(0,wheight//2),(wwidth-1,wheight//2),(255,255,0),1)

                x=int(round(wwidth/2+wwidth/2*self.imu_acl_y))
                y=int(round(wheight/2))
                cv2.circle(img,(x ,y),2,(0,255,0),-1)
                x=int(round(wwidth/2))
                y=int(round(wheight/2+wheight/2*self.imu_acl_x))
                cv2.circle(img,(x ,y),2,(0,255,0),-1)

                x=int(round(wwidth/2+wwidth/2*self.imu_gyr_x))
                y=int(round(wheight/2))
                cv2.circle(img,(x ,y),2,(255,0,0),-1)
                x=int(round(wwidth/2))
                y=int(round(wheight/2+wheight/2*self.imu_gyr_y))
                cv2.circle(img,(x ,y),2,(255,0,0),-1)

                x=int(round(wwidth/2+wwidth/2*self.imu_gyr_z))
                y=int(round(wheight/2))
                cv2.circle(img,(x ,y),2,(0,0,255),-1)

        if self.cfg.HAVE_INA226:
            cv2.putText(img,"{:.2f}".format(self.volt_b),(0,wheight-11),textFontFace,textFontScale,textColor,textThickness)
            cv2.putText(img,"{:.2f}".format(self.volt_a),(0,wheight-1),textFontFace,textFontScale,textColor,textThickness)

        if self.cfg.HAVE_ADS1115:
            cv2.circle(img,(wwidth//4*1,wheight//2),int(self.dist2*40),(0,255,0),1)
            cv2.circle(img,(wwidth//4*2,wheight//2),int(self.dist0*40),(0,255,0),1)
            cv2.circle(img,(wwidth//4*3,wheight//2),int(self.dist1*40),(0,255,0),1)

        if self.cfg.HAVE_VL53L0X:
            def distColor(dist):
                if dist > self.dist_slow:
                    return (0,255,0)
                elif dist > self.dist_stop:
                    return (255,255,0)
                else:
                    return (255,0,0)

            '''
            cv2.circle(img,(wwidth//4*2,wheight//4*2),int(self.dist0*40),distColor(self.dist0),1)
            cv2.circle(img,(wwidth//6*1,wheight//4*2),int(self.dist1*40),distColor(self.dist1),1)
            cv2.circle(img,(wwidth//6*5,wheight//4*2),int(self.dist2*40),distColor(self.dist2),1)
            cv2.circle(img,(wwidth//6*2,wheight//4*3),int(self.dist3*40),distColor(self.dist3),1)
            cv2.circle(img,(wwidth//6*4,wheight//4*3),int(self.dist4*40),distColor(self.dist4),1)
            cv2.circle(img,(wwidth//4*1,wheight//4*1),int(self.dist5*40),distColor(self.dist5),1)
            cv2.circle(img,(wwidth//4*3,wheight//4*1),int(self.dist6*40),distColor(self.dist6),1)

            cv2.putText(img,"0",(wwidth//4*2,wheight//4*2),textFontFace,textFontScale,textColor,textThickness)
            cv2.putText(img,"1",(wwidth//6*1,wheight//4*2),textFontFace,textFontScale,textColor,textThickness)
            cv2.putText(img,"2",(wwidth//6*5,wheight//4*2),textFontFace,textFontScale,textColor,textThickness)
            cv2.putText(img,"3",(wwidth//6*2,wheight//4*3),textFontFace,textFontScale,textColor,textThickness)
            cv2.putText(img,"4",(wwidth//6*4,wheight//4*3),textFontFace,textFontScale,textColor,textThickness)
            cv2.putText(img,"5",(wwidth//4*1,wheight//4*1),textFontFace,textFontScale,textColor,textThickness)
            cv2.putText(img,"6",(wwidth//4*3,wheight//4*1),textFontFace,textFontScale,textColor,textThickness)
            '''
            x = int(wwidth/2 * (1 + self.angle * 0.75))
            cv2.circle(img,(x,wheight//2),int(self.dist0*40),distColor(self.dist4),1)
            if self.dist4 == 65535:
                cv2.putText(img,"ERROR",(x,wheight//2),textFontFace,textFontScale,(255,0,0),textThickness)
            elif self.dist4 < 8190:
                #xx = (80-int(self.dist4*80/1200))//2
                #cv2.line(img,(x-xx,wheight//3*2),(x+xx,wheight//3*2),distColor(self.dist4),2)
                cv2.putText(img,str(self.dist4),(x,wheight//2),textFontFace,textFontScale,distColor(self.dist4),textThickness)

            '''
            cv2.circle(img,(wwidth//6*1,wheight//5*3),int(self.dist1*40),distColor(self.dist5),1)
            if self.dist5 < 8190:
                #cv2.line(img,(0,wheight//4*3),(80-int(self.dist5*80/1200),wheight//4*3),(255,255,255),4)
                #cv2.line(img,(0,wheight//4*3),(80-int(self.dist5*80/1200),wheight//4*3),(0,0,0),2)
                cv2.putText(img,str(self.dist5),(wwidth//6*1,wheight//5*3),textFontFace,textFontScale,distColor(self.dist5),textThickness)
            cv2.circle(img,(wwidth//6*5,wheight//5*3),int(self.dist2*40),distColor(self.dist6),1)
            if self.dist6 < 8190:
                #cv2.line(img,(wwidth-1,wheight//4*3),(80+int(self.dist6*80/1200),wheight//4*3),(255,255,255),4)
                #cv2.line(img,(wwidth-1,wheight//4*3),(80+int(self.dist6*80/1200),wheight//4*3),(0,0,0),2)
                cv2.putText(img,str(self.dist6),(wwidth//6*5,wheight//5*3),textFontFace,textFontScale,distColor(self.dist6),textThickness)
            '''

        if self.period_time - 1 > 1000 / self.cfg.DRIVE_LOOP_HZ:
            period_color = (255,0,0) #red
        else:
            period_color = (0,255,0) #green

        if self.period_time > 99.9:
            pos = (159-3*8,wheight-1)
        elif self.period_time > 9.9:
            pos = (159-2*8,wheight-1)
        else:
            pos = (159-1*8,wheight-1)
        cv2.putText(img,str(int(self.period_time)),pos,textFontFace,textFontScale,period_color,textThickness)

        if self.fullscreen:
            cv2.resizeWindow("DonkeyCamera",wwidth*3,wheight*3)
            #cv2.setWindowProperty('DonkeyCamera', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            cv2.resizeWindow("DonkeyCamera",wwidth,wheight)
            #cv2.setWindowProperty('DonkeyCamera', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
        cv2.imshow('DonkeyCamera', img[:,:,::-1])

        wk = cv2.waitKey(1) & 0xff
        #if wk != 255:
        #    print(wk)
        if wk == ord('q') or wk == 99 or wk == 27: # ctrl-c esc
            cv2.destroyAllWindows()
            self.on = False
        #elif wk == ord('w'):
        #    if self.fullscreen:
        #        self.fullscreen = False
        #    else:
        #        self.fullscreen = True
        #elif wk == ord('g'):
        #    if self.disp_imu:
        #        self.disp_imu = False
        #    else:
        #        self.disp_imu = True
        elif wk == ord('s'):
            if self.disp_callsign:
                self.disp_callsign = False
            else:
                self.disp_callsign = True
        elif wk == ord('p'):
            self.q_button.put([99,'p'])
        elif wk == ord('P'):
            self.q_button.put([99,'P'])
        elif wk == ord('r'):
            self.q_button.put([99,'r'])
        elif wk == ord('R'):
            self.q_button.put([99,'R'])
        elif wk == ord('u'):
            self.q_button.put([99,'u'])
        elif wk == ord('l'):
            self.q_button.put([99,'l'])
        elif wk == ord('/') or wk == 175:
            self.q_button.put([99,'/'])
        elif wk == ord('=') or wk == 157:
            self.q_button.put([99,'='])
        elif wk == ord('9') or wk == 185:
            self.q_button.put([99,'9'])
        elif wk == ord('8') or wk == 184:
            self.q_button.put([99,'8'])
        elif wk == ord('6') or wk == 182:
            self.q_button.put([99,'6'])
        elif wk == ord('5') or wk == 181:
            self.q_button.put([99,'5'])
        elif wk == ord('3') or wk == 179:
            self.q_button.put([99,'3'])
        elif wk == ord('2') or wk == 178:
            self.q_button.put([99,'2'])
        elif wk == ord('.') or wk == 174:
            self.q_button.put([99,'.'])
        elif wk == ord('0') or wk == 176:
            self.q_button.put([99,'0'])
        elif wk == ord('+') or wk == 171:
            self.q_button.put([99,'+'])
        elif wk == ord('-') or wk == 173:
            self.q_button.put([99,'-'])

    def shutdown(self):
        self.on = False
        GPIO.cleanup()
        print("FPVDisp shutdown")

    #def __del__(self):
    #    cv2.destroyAllWindows()
