import moviepy.editor as mpy
from tensorflow.python.keras import activations
from tensorflow.python.keras import backend as K

try:
    from vis.visualization import visualize_saliency, overlay
    from vis.utils import utils
    from vis.backprop_modifiers import get
    from vis.losses import ActivationMaximization
    from vis.optimizer import Optimizer
except:
    raise Exception("Please install keras-vis: pip install git+https://github.com/autorope/keras-vis.git")

import donkeycar as dk
from donkeycar.parts.datastore import Tub
from donkeycar.utils import *


class MakeMovie(object):
    def __init__(self):
        self.deg_to_rad = math.pi / 180.0

    def run(self, args, parser):
        '''
        Load the images from a tub and create a movie from them.
        Movie
        '''

        if args.tub is None:
            print("ERR>> --tub argument missing.")
            parser.print_help()
            return

        conf = os.path.expanduser(args.config)
        if not os.path.exists(conf):
            print("No config file at location: %s. Add --config to specify\
                 location or run from dir containing config.py." % conf)
            return

        self.cfg = dk.load_config(conf)

        if args.type is None and args.model is not None:
            args.type = self.cfg.DEFAULT_MODEL_TYPE
            print("Model type not provided. Using default model type from config file")

        if args.salient:
            if args.model is None:
                print("ERR>> salient visualization requires a model. Pass with the --model arg.")
                parser.print_help()

            if args.type not in ['linear', 'categorical']:
                print("Model type {} is not supported. Only linear or categorical is supported for salient visualization".format(args.type))
                parser.print_help()
                return

        self.tub = Tub(args.tub)
        self.index = self.tub.get_index(shuffled=False)
        start = args.start
        self.end = args.end if args.end != -1 else len(self.index)
        if self.end >= len(self.index):
            self.end = len(self.index) - 1
        num_frames = self.end - start
        self.iRec = start
        self.scale = args.scale
        self.keras_part = None
        self.do_salient = False
        if args.model is not None:
            self.keras_part = get_model_by_type(args.type, cfg=self.cfg)
            self.keras_part.load(args.model)
            self.keras_part.compile()
            if args.salient:
                self.do_salient = self.init_salient(self.keras_part.model)

        print('making movie', args.out, 'from', num_frames, 'images')

        import csv
        try:
            f = open('/run/shm/mycar/data/log.csv','r')
            self.csv = [row for row in csv.reader(f)]
            self.csv_file = True

            row = self.csv[0]
            n = 0
            self.dic = {}
            for d in row:
                self.dic[row[n]] = n
                n += 1
        except:
            self.csv_file = False

        if self.csv_file == False:
            clip = mpy.VideoClip(self.make_frame,
                                 duration=((num_frames - 1) / self.cfg.DRIVE_LOOP_HZ))
            clip.write_videofile(args.out, fps=self.cfg.DRIVE_LOOP_HZ)
        else:
            '''
            i = self.dic["ms"]
            duration = 0
            for d in self.csv:
                row = self.csv[n]
                duration += float(row[i])
            duration /= 1000
            print('duration = ', duration)
            '''
            record_start = self.tub.get_record(self.index[start])
            record_last = self.tub.get_record(self.index[self.end])
            duration = (int(record_last["milliseconds"]) - int(record_start["milliseconds"])) / 1000
            print('duration = ', duration)

            clip = mpy.VideoClip(self.make_frame,
                                 duration=duration)
            clip.write_videofile(args.out, fps=(num_frames - 1) / duration)

    def draw_user_input(self, record, img):
        '''
        Draw the user input as a green line on the image
        '''

        import cv2

        user_angle = float(record["user/angle"])
        user_throttle = float(record["user/throttle"])

        try:
            if record["user/mode"] == "local_angle":
                user_angle = float(record["pilot/angle"])
            elif record["user/mode"] == "local":
                user_angle = float(record["pilot/angle"])
                user_throttle = float(record["pilot/throttle"])
        except:
            pass

        height, width, _ = img.shape

        '''
        length = height
        a1 = user_angle * 45.0
        l1 = user_throttle * length

        mid = width // 2 - 1

        p1 = tuple((mid - 2, height - 1))
        p11 = tuple((int(p1[0] + l1 * math.cos((a1 + 270.0) * self.deg_to_rad)),
                     int(p1[1] + l1 * math.sin((a1 + 270.0) * self.deg_to_rad))))
        '''
        user_angle *= self.cfg.CONTROLLER_ANGLE_NR
        user_throttle *= self.cfg.CONTROLLER_THROTTLE_NR
        p1 = tuple((int(round(width/2)), int(round(height))))
        p11 = tuple((int(round(width/2 + width/2 * user_angle)),
                    int(round(height + height * user_throttle))))

        # user is green, pilot is blue
        cv2.line(img, p1, p11, (0, 255, 0), 2)

        def printText(img, str, xy, textColor=(0,255,0)):
            textFontFace = cv2.FONT_HERSHEY_SIMPLEX
            textFontScale = 0.4
            textThickness = 1
            cv2.putText(img, str, xy, textFontFace,textFontScale,textColor,textThickness)

        printText(img, record["user/mode"], (0,9))
        printText(img, str(self.iRec), (120,9))

        if self.csv_file == True:
            row = self.csv[self.iRec + 1]

            i = self.dic["ms"]
            cycle_time = float(row[i])
            printText(img, "{:.1f}".format(cycle_time), (width-8*7//2,height-1))

            if self.cfg.HAVE_INA226:
                i = self.dic["va"]
                volt_a = "{:.2f}".format(float(row[i]))
                printText(img, volt_a, (0,height-1))
                i = self.dic["vb"]
                volt_b = "{:.2f}".format(float(row[i]))
                printText(img, volt_b, (0,height-11))

            if self.cfg.HAVE_REVCOUNT:
                i = self.dic["lap"]
                lap = row[i]
                printText(img, lap, (0,height-21))

                i = self.dic["kmph"]
                kmph = "{:.1f}".format(float(row[i]))
                printText(img, kmph, (40,height-1))

                i = self.dic["rpm"]
                rpm = row[i]
                printText(img, rpm, (90,height-1))

                i = self.dic["odo"]
                rpm = row[i]
                printText(img, rpm, (40,height-21))

            try:
                i = self.dic["gyro_gain"]
                gyro_gain = row[i]
                printText(img, gyro_gain, (0,39))
            except:
                pass

            try:
                i = self.dic["ai_throttle_mult"]
                ai_throttle_mult = "{:.2f}".format(float(row[i]))
                printText(img, ai_throttle_mult, (0,29))
            except:
                pass

            if self.cfg.HAVE_LIDAR:
                i = self.dic["stop_range"]
                stop_range = row[i]
                printText(img, stop_range,(0,49))

                i = self.dic["lidar"]
                lidar = row[i]
                printText(img, lidar,(0,59))

            try:
                i = self.dic["throttle_scale"]
                throttle_scale = "{:.2f}".format(float(row[i]))
                printText(img, throttle_scale,(0,19))
            except:
                pass

        
    def draw_model_prediction(self, record, img):
        '''
        query the model for it's prediction, draw the predictions
        as a blue line on the image
        '''
        if self.keras_part is None:
            return

        import cv2
         
        expected = self.keras_part.model.inputs[0].shape[1:]
        actual = img.shape

        # normalize image before prediction
        pred_img = img.astype(np.float32) / 255.0

        # check input depth
        if expected[2] == 1 and actual[2] == 3:
            pred_img = rgb2gray(pred_img)
            pred_img = pred_img.reshape(pred_img.shape + (1,))
            actual = pred_img.shape

        if expected != actual:
            print("expected input dim", expected, "didn't match actual dim", actual)
            return

        pilot_angle, pilot_throttle = self.keras_part.run(pred_img)
        height, width, _ = pred_img.shape

        length = height
        a2 = pilot_angle * 45.0
        l2 = pilot_throttle * length

        mid = width // 2 - 1

        p2 = tuple((mid + 2, height - 1))
        p22 = tuple((int(p2[0] + l2 * math.cos((a2 + 270.0) * self.deg_to_rad)),
                     int(p2[1] + l2 * math.sin((a2 + 270.0) * self.deg_to_rad))))

        # user is green, pilot is blue
        #cv2.line(img, p2, p22, (0, 0, 255), 2)

    def draw_steering_distribution(self, record, img):
        '''
        query the model for it's prediction, draw the distribution of steering choices
        '''
        from donkeycar.parts.keras import KerasCategorical

        if self.keras_part is None or type(self.keras_part) is not KerasCategorical:
            return

        import cv2

        pred_img = img.reshape((1,) + img.shape)
        angle_binned, _ = self.keras_part.model.predict(pred_img)

        x = 4
        dx = 4
        y = 120 - 4
        iArgMax = np.argmax(angle_binned)
        for i in range(15):
            p1 = (x, y)
            p2 = (x, y - int(angle_binned[0][i] * 100.0))
            if i == iArgMax:
                cv2.line(img, p1, p2, (255, 0, 0), 2)
            else:
                cv2.line(img, p1, p2, (200, 200, 200), 2)
            x += dx

    def init_salient(self, model):
        # Utility to search for layer index by name. 
        # Alternatively we can specify this as -1 since it corresponds to the last layer.
        first_output_name = None
        for i, layer in enumerate(model.layers):
            if first_output_name is None and "dropout" not in layer.name.lower() and "out" in layer.name.lower():
                first_output_name = layer.name
                layer_idx = i

        if first_output_name is None:
            print("Failed to find the model layer named with 'out'. Skipping salient.")
            return False

        print("####################")
        print("Visualizing activations on layer:", first_output_name)
        print("####################")
        
        # ensure we have linear activation
        model.layers[layer_idx].activation = activations.linear
        # build salient model and optimizer
        sal_model = utils.apply_modifications(model)
        modifier_fn = get('guided')
        sal_model_mod = modifier_fn(sal_model)
        losses = [
            (ActivationMaximization(sal_model_mod.layers[layer_idx], None), -1)
        ]
        self.opt = Optimizer(sal_model_mod.input, losses, norm_grads=False)
        return True

    def compute_visualisation_mask(self, img):
        grad_modifier = 'absolute'
        grads = self.opt.minimize(seed_input=img, max_iter=1, grad_modifier=grad_modifier, verbose=False)[1]
        channel_idx = 1 if K.image_data_format() == 'channels_first' else -1
        grads = np.max(grads, axis=channel_idx)
        res = utils.normalize(grads)[0]
        return res

    def draw_salient(self, img):
        import cv2
        alpha = 0.004
        beta = 1.0 - alpha

        expected = self.keras_part.model.inputs[0].shape[1:]
        actual = img.shape
        pred_img = img.astype(np.float32) / 255.0

        # check input depth
        if expected[2] == 1 and actual[2] == 3:
            pred_img = rgb2gray(pred_img)
            pred_img = pred_img.reshape(pred_img.shape + (1,))

        salient_mask = self.compute_visualisation_mask(pred_img)
        z = np.zeros_like(salient_mask)
        salient_mask_stacked = np.dstack((z, z))
        salient_mask_stacked = np.dstack((salient_mask_stacked, salient_mask))
        blend = cv2.addWeighted(img.astype('float32'), alpha, salient_mask_stacked, beta, 0.0)
        return blend

    def make_frame(self, t):
        '''
        Callback to return an image from from our tub records.
        This is called from the VideoClip as it references a time.
        We don't use t to reference the frame, but instead increment
        a frame counter. This assumes sequential access.
        '''

        if self.iRec >= self.end or self.iRec >= len(self.index):
            return None

        rec_ix = self.index[self.iRec]
        rec = self.tub.get_record(rec_ix)
        image = rec['cam/image_array']

        if self.cfg.ROI_CROP_TOP != 0 or self.cfg.ROI_CROP_BOTTOM != 0:
            image = img_crop(image, self.cfg.ROI_CROP_TOP, self.cfg.ROI_CROP_BOTTOM)

        if self.do_salient:
            image = self.draw_salient(image)
            image = image * 255
            image = image.astype('uint8')
        
        self.draw_user_input(rec, image)
        if self.keras_part is not None:
            self.draw_model_prediction(rec, image)
            self.draw_steering_distribution(rec, image)

        if self.scale != 1:
            import cv2
            h, w, d = image.shape
            dsize = (w * self.scale, h * self.scale)
            image = cv2.resize(image, dsize=dsize, interpolation=cv2.INTER_CUBIC)

        self.iRec += 1
        # returns a 8-bit RGB array
        return image
