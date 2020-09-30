# import keras
import keras

# import keras_retinanet
from keras_retinanet import models
from keras_retinanet.utils.image import read_image_bgr, preprocess_image, resize_image
from keras_retinanet.utils.visualization import draw_box, draw_caption
from keras_retinanet.utils.colors import label_color

# import miscellaneous modules
import matplotlib.pyplot as plt
import cv2
import os
import numpy as np
from PIL import Image

# set tf backend to allow memory to grow, instead of claiming everything
import tensorflow as tf

def get_session():
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    return tf.Session(config=config)

# set the modified tf session as backend in keras
keras.backend.tensorflow_backend.set_session(get_session())

# adjust this to point to your downloaded/trained model
model_path = '/home/kamiar/projects/opervu/inference/model.h5'

# load retinanet model
model = models.load_model(model_path, backbone_name='resnet50')

# if the model is not converted to an inference model, use the line below
#model = models.convert_model(model)

#print(model.summary())

# load label to names mapping for visualization purposes
labels_to_names = {0: 'forceps',
1: 'clamp',
2: 'scalpel',
3: 'sponge',
4: 'gauze',
5: 'woods pack',
6: 'needle',
7: 'needle holder',
8: 'sucker',
9: 'glove',
10: 'incision',
11: 'obstruction',
12: 'bovie'}

# init circulare frame cotainer
frames = []
frame_ptr = 0
frame = {0:[], 1:[], 2:[], 6:[], 7:[], 8:[]}
for i in range(10):
    frames.append(frame)

# indicator for very first frames
first_frame = True

# frame that holds tracking pred_info
t_frame = {0:[], 1:[], 2:[], 6:[], 7:[], 8:[]}

# ID counter for tracked SI
tracked_SI_ID_counter = 0


#PATH_TO_VIDEO = '/home/kamiar/Videos/opervu_videos/Children_Hosp_9-18/Surgery_1.avi'
PATH_TO_VIDEO = '/home/kamiar/Videos/opervu_videos/Children_Hosp_9-18/cut1.avi'
# Open video file
vidcap = cv2.VideoCapture(PATH_TO_VIDEO)

def predict_first():
    if vidcap.isOpened():
        # Acquire frame and expand frame dimensions to have shape: [1, None, None, 3]
        # i.e. a single-column array, where each item in the column has the pixel RGB value
        success, image = vidcap.read()

        if success:
            # copy to draw on
            draw = image.copy()
            draw = cv2.cvtColor(draw, cv2.COLOR_BGR2RGB)

            # preprocess image for network
            image = preprocess_image(image)
            image, scale = resize_image(image)

            # process image
            boxes, scores, labels = model.predict_on_batch(np.expand_dims(image, axis=0))

            # correct for image scale
            boxes /= scale

            pred_info = {'SI':'', 'Trk ID':'', 'VxVy':'', 'BBox':'', 'Score':''}

            # init SI containers for this frame
            frame = {0:[], 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[], 9:[], 10:[], 11:[], 12:[]}

            # visualize detections
            for box, score, label in zip(boxes[0], scores[0], labels[0]):
                # scores are sorted so we can break
                if score < 0.5:
                    break

                i_box = list(int(box[0]), int(box[1]), int(box[2]), int(box[3]))
                i_center = list((i_box[0] + i_box[2]) / 2, (i_box[1] + i_box[3]) / 2)
                i_score = int(score * 100)
                frame[label].append({'i': -1, 'b':i_box, 's':i_score, 'c':i_center, 'v':[float('nan'), float('nan')])

                # prediction info
                pred_info['SI'] += "{}\n".format(labels_to_names[label])
                pred_info['Trk ID'] += "{}\n".format(1)
                pred_info['VxVy'] += "[{:3d}, {:3d}]\n".format(100, 100)
                pred_info['BBox'] += "[{:4d}, {:4d}, {:4d}, {:4d}]\n".format(i_box[0], i_box[1], i_box[2], i_box[3])
                pred_info['Score'] += "{:3d}\n".format(i_score)

                color = label_color(label)

                b = box.astype(int)
                draw_box(draw, b, color=color)

                caption = "{} {:.3f}".format(labels_to_names[label], score)
                draw_caption(draw, b, caption)

                #resized = cv2.resize(draw, (1024, 1024))

                # All the results have been drawn on the frame, so it's time to display it.
                #cv2.imshow('Object detector', resized)

            # add SIs to the frames
            if frame_ptr == 10:
                frame_ptr = 0
            frames[frame_ptr] = frame
            frame_ptr += 1

            track_SIs()

            return draw, pred_info
            # Press 'q' to quit
            #if cv2.waitKey(1) == ord('q'):
                #break

def track_SIs():
    if first_frame and frame_ptr < 2:
        return

    first_frame = False

    for si in frames[frame_ptr - 1].keys():
        for si_item in si:


def predict_next():
    while(vidcap.isOpened()):
        # Acquire frame and expand frame dimensions to have shape: [1, None, None, 3]
        # i.e. a single-column array, where each item in the column has the pixel RGB value
        success, image = vidcap.read()

        if success:
            # copy to draw on
            draw = image.copy()
            #draw = cv2.cvtColor(draw, cv2.COLOR_BGR2RGB)

            # preprocess image for network
            image = preprocess_image(image)
            image, scale = resize_image(image)

            # process image
            boxes, scores, labels = model.predict_on_batch(np.expand_dims(image, axis=0))

            # correct for image scale
            boxes /= scale

            # visualize detections
            for box, score, label in zip(boxes[0], scores[0], labels[0]):
                # scores are sorted so we can break
                if score < 0.5:
                    break


                color = label_color(label)

                b = box.astype(int)
                draw_box(draw, b, color=color)

                caption = "{} {:.3f}".format(labels_to_names[label], score)
                draw_caption(draw, b, caption)

                resized = cv2.resize(draw, (1024, 1024))

                # All the results have been drawn on the frame, so it's time to display it.
                cv2.imshow('Object detector', resized)

                # Press 'q' to quit
                if cv2.waitKey(1) == ord('q'):
                    break

        else:
            break

def quit():
    cv2.destroyAllWindows()
    vidcap.release()
