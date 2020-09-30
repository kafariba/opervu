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
import math
import numpy as np
from PIL import Image

# set tf backend to allow memory to grow, instead of claiming everything
import tensorflow as tf

# The linear sum assignment problem is also known as minimum weight matching in bipartite graphs
from scipy.optimize import linear_sum_assignment

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
frames_ptr = 0
frame = {0:[], 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[], 9:[], 10:[], 11:[], 12:[]}
for i in range(10):
    frames.append(frame)

# indicator for very first frames
first_frame = True

# frame that holds tracking pred_info
t_frame = {0:[], 1:[], 2:[], 6:[], 7:[], 8:[]}

# ID counter for tracked SI
id_counter = 0

# max num pixels that an instrument can travel from frame to frame
MAX_VEL = 400

#PATH_TO_VIDEO = '/home/kamiar/Videos/opervu_videos/Children_Hosp_9-18/Surgery_1.avi'
PATH_TO_VIDEO = '/home/kamiar/Videos/opervu_videos/Children_Hosp_9-18/cut1.avi'
# Open video file
vidcap = cv2.VideoCapture(PATH_TO_VIDEO)

def predict_first():
    global frames_ptr
    global frames

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

            # init SI containers for this frame
            frame = {0:[], 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[], 9:[], 10:[], 11:[], 12:[]}

            # visualize detections
            for box, score, label in zip(boxes[0], scores[0], labels[0]):
                # scores are sorted so we can break
                if score < 0.5:
                    break

                i_box = [int(box[0]), int(box[1]), int(box[2]), int(box[3])]
                i_center = box_center(i_box)
                i_score = int(score * 100)
                # max vel(Vx,Vy) = +/- 300-400 pix per o.1 sec
                frame[label].append({'id': -1, 'box':i_box, 'scr':i_score, 'cen':i_center,
                        'vel-est':[float('nan'), float('nan')], 'vel-act':[float('nan'), float('nan')]})

                color = label_color(label)

                b = box.astype(int)
                draw_box(draw, b, color=color)

                caption = "{} {:.3f}".format(labels_to_names[label], score)
                draw_caption(draw, b, caption)

                #resized = cv2.resize(draw, (1024, 1024))

                # All the results have been drawn on the frame, so it's time to display it.
                #cv2.imshow('Object detector', resized)

            # add SIs to the frames
            if frames_ptr == 10:
                frames_ptr = 0
            frames[frames_ptr] = frame
            frames_ptr += 1

            track_SIs()

            pred_info = {'si':'', 'id':'', 'box':'', 'scr':'', 'cen':'', 'vel-est':'', 'vel-act':''}

            for si in frames[frames_ptr - 1]:
                for si_item in frames[frames_ptr - 1][si]:
                    pred_info['si'] += "{}\n".format(labels_to_names[si])
                    pred_info['id'] += "{}\n".format(si_item['id'])
                    pred_info['box'] += "[{:4d}, {:4d}, {:4d}, {:4d}]\n".format(si_item['box'][0], si_item['box'][1], si_item['box'][2], si_item['box'][3])
                    pred_info['scr'] += "{:3d}\n".format(si_item['scr'])
                    pred_info['cen'] += "[{:3d}, {:3d}]\n".format(si_item['cen'][0], si_item['cen'][1])
                    pred_info['vel-est'] += "[{:3}, {:3}]\n".format(si_item['vel-est'][0], si_item['vel-est'][1])
                    pred_info['vel-act'] += "[{:3}, {:3}]\n".format(si_item['vel-act'][0], si_item['vel-act'][1])



            return draw, pred_info
            # Press 'q' to quit
            #if cv2.waitKey(1) == ord('q'):
                #break

def box_center(box):
    # returns the center of the given rect. box
    return [round((box[0] + box[2]) / 2), round((box[1] + box[3]) / 2)]

def calc_vel(center1, center2):
    # calc vel from the given centers
    return [(center1[0] - center2[0]), (center1[1] - center2[1])]

def calc_dist(pt1, pt2):
    # retrun dist btw two points
    return (round(math.sqrt((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)))

def calc_min_dist(si):
    # return the SI set in the old frame that are closest the new frame
    global frames
    global frames_ptr

    cost_mtx = []
    for si_item_a in frames[frames_ptr - 1][si]:
        cost_mtx_row = []
        for si_item_b in frames[frames_ptr - 2][si]:
            cost_mtx_row.append(calc_dist(si_item_a['cen'], si_item_b['cen']))
        cost_mtx.append(cost_mtx_row)

    row_ind, col_ind = linear_sum_assignment(cost_mtx)
    return row_ind, col_ind


def track_SIs():
    global id_counter
    global frames
    global frames_ptr
    global first_frame

    if first_frame:
        if frames_ptr == 1:
            # first time in tracking, init ID's incrementally from 0
            for si in frames[0].keys():
                for si_item in frames[0][si]:
                    si_item['id'] = id_counter
                    id_counter += 1
            return

        elif frames_ptr == 2:
            # the first two frames seen.
            first_frame = False

    for si in frames[frames_ptr - 1].keys():
        # for each SI
        if len(frames[frames_ptr - 1][si]) == 0:
            # no SI
            continue
        elif len(frames[frames_ptr - 1][si]) == 1:
            if len(frames[frames_ptr - 2][si]) == 0:
                # if 1 si item in frame 1 but not in frame 0,
                # assign a new id
                frames[frames_ptr - 1][si][0]['id'] = id_counter
                id_counter += 1
            elif len(frames[frames_ptr - 2][si]) == 1:
                # if only 1 of the same si item in both frames,
                # then they are the same si if within range
                vel =  calc_vel(frames[frames_ptr - 1][si][0]['cen'], frames[frames_ptr - 2][si][0]['cen'])
                if abs(vel[0]) < MAX_VEL and abs(vel[1]) < MAX_VEL:
                    frames[frames_ptr - 1][si][0]['id'] = frames[frames_ptr - 2][si][0]['id']
                    frames[frames_ptr - 1][si][0]['vel-est'] = frames[frames_ptr - 2][si][0]['vel-act']
                    frames[frames_ptr - 1][si][0]['vel-act'] = vel
                else:
                    # new SI
                    frames[frames_ptr - 1][si][0]['id'] = id_counter
                    id_counter += 1
        else:
            # more than 1 of same SI's in prev frame
            # find the matching SI in prev frame
            cur_set_ind, prev_set_ind = calc_min_dist(si)
            for cur_i, prev_i in zip(cur_set_ind, prev_set_ind):
                vel =  calc_vel(frames[frames_ptr - 1][si][cur_i]['cen'], frames[frames_ptr - 2][si][prev_i]['cen'])
                if abs(vel[0]) < MAX_VEL and abs(vel[1]) < MAX_VEL:
                    frames[frames_ptr - 1][si][cur_i]['id'] = frames[frames_ptr - 2][si][prev_i]['id']
                    frames[frames_ptr - 1][si][cur_i]['vel-est'] = frames[frames_ptr - 2][si][prev_i]['vel-act']
                    frames[frames_ptr - 1][si][cur_i]['vel-act'] = vel
                else:
                    # new SI
                    frames[frames_ptr - 1][si][cur_i]['id'] = id_counter
                    id_counter += 1


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
