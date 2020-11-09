#!/usr/bin/python3


# import keras
from tensorflow import keras

# import keras_retinanet
from keras_retinanet import models
from keras_retinanet.utils.image import read_image_bgr, preprocess_image, resize_image
from keras_retinanet.utils.visualization import draw_box, draw_caption
from keras_retinanet.utils.colors import label_color
from keras_retinanet.utils.gpu import setup_gpu

# import miscellaneous modules
import matplotlib.pyplot as plt
import cv2
import os
import numpy as np
import time
import math
from PIL import Image
from collections import deque

# set tf backend to allow memory to grow, instead of claiming everything
import tensorflow as tf

# The linear sum assignment problem is also known as minimum weight matching in bipartite graphs
from scipy.optimize import linear_sum_assignment

# use this to change which GPU to use
gpu = '0'

# set the modified tf session as backend in keras
setup_gpu(gpu)

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

# name to label mapping
names_to_labels = {'forceps': 0,
'clamp': 1,
'scalpel': 2,
'sponge': 3,
'gauze': 4,
'woods pack': 5,
'needle': 6,
'needle holder': 7,
'sucker': 8,
'glove': 9,
'incision': 10,
'obstruction': 11,
'bovie': 12}

# minimum confidence score for each detected label
min_SI_scores = {0: 0.5,
1: 0.5,
2: 0.45,
3: 0.5,
4: 0.55,
5: 0.5,
6: 0.55,
7: 0.5,
8: 0.55,
9: 0.7,
10: 0.78,
11: 0.72,
12: 0.6}

# init circulare frame cotainer
frames = []
frames_ptr = 0
frame = {0:[], 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[], 9:[], 10:[], 11:[], 12:[]}
for i in range(10):
    frames.append(frame)

# exp weighted avg constant ~ 5 frame avg
BETA = 0.8

# init value for exp wgt avg
ewa_init_box = np.array([0, 0, 0, 0])

# incision ewa box
incision_ewa_box = ewa_init_box.copy()

incision_q = deque(maxlen=300)

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
                if score < min_SI_scores[label]:
                    break

                i_box = np.array([int(box[0]), int(box[1]), int(box[2]), int(box[3])])
                i_center = box_center(i_box)
                i_score = int(score * 100)

                # for incision calc exp wgt avg (ewa) and put into cirular buf(300)

                # max vel(Vx,Vy) = +/- 300-400 pix per 0.1 sec
                frame[label].append({'id': -1, 'trk_cnt': 0, 'link_id': -1, 'link_cnt': 0, 'box':i_box,
                                        'box_ewa':ewa_init_box, 'scr':i_score, 'cen':i_center,
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

            # assign id/link id: correlate SIs from consecutive frames, link enclosing SIs (glove & forceps)
            track_SIs()

            pred_info = {'si':'', 'id':'', 'box':'', 'scr':'', 'cen':'', 'vel-est':'', 'vel-act':''}

            for si in frames[frames_ptr]:
                for si_item in frames[frames_ptr][si]:
                    pred_info['si'] += "{}\n".format(labels_to_names[si])
                    pred_info['id'] += "{}:{}:{}\n".format(si_item['id'], si_item['link_id'], si_item['link_cnt'])
                    pred_info['box'] += "[{:4d}, {:4d}, {:4d}, {:4d}]\n".format(si_item['box'][0], si_item['box'][1], si_item['box'][2], si_item['box'][3])
                    pred_info['scr'] += "{:3d}\n".format(si_item['scr'])
                    pred_info['cen'] += "[{:3d}, {:3d}]\n".format(si_item['cen'][0], si_item['cen'][1])
                    pred_info['vel-est'] += "[{:3}, {:3}]\n".format(si_item['vel-est'][0], si_item['vel-est'][1])
                    pred_info['vel-act'] += "[{:3}, {:3}]\n".format(si_item['vel-act'][0], si_item['vel-act'][1])


            frames_ptr += 1
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
    for si_item_a in frames[frames_ptr][si]:
        cost_mtx_row = []
        for si_item_b in frames[frames_ptr - 1][si]:
            cost_mtx_row.append(calc_dist(si_item_a['cen'], si_item_b['cen']))
        cost_mtx.append(cost_mtx_row)

    row_ind, col_ind = linear_sum_assignment(cost_mtx)
    return row_ind, col_ind

def calc_iou(box_a, box_b):
    # x & y of intersection rect.
    x_a = max(box_a[0], box_b[0])
    y_a = max(box_a[1], box_b[1])
    x_b = min(box_a[2], box_b[2])
    y_b = min(box_a[3], box_b[3])

    #cal intersection area
    inter_area = max(0, x_b - x_a) * max(0, y_b - y_a)

    #cal area of both boxes
    box_a_area = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
    box_b_area = (box_b[2] - box_b[0]) * (box_b[3] - box_b[1])

    #cal iou
    return inter_area / (box_a_area + box_b_area - inter_area)

def calc_ioa(box_a, box_b):
    #calculate intersection over box_a

    # x & y of intersection rect.
    x_a = max(box_a[0], box_b[0])
    y_a = max(box_a[1], box_b[1])
    x_b = min(box_a[2], box_b[2])
    y_b = min(box_a[3], box_b[3])

    #cal intersection area
    inter_area = max(0, x_b - x_a) * max(0, y_b - y_a)
    print(inter_area)

    #cal area of box a
    box_a_area = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
    print(box_a_area)

    #cal iou
    return inter_area / box_a_area

def track_SIs():
    global id_counter
    global frames
    global frames_ptr
    global first_frame

    if first_frame:
        # first time in tracking, init ID's incrementally from 0
        first_frame = False
        for si in frames[0].keys():
            for si_item in frames[0][si]:
                si_item['id'] = id_counter
                id_counter += 1
        return



    for si in frames[frames_ptr].keys():
        # not tracking incision
        if si == names_to_labels['incision']:
            # for incision calculate ewa, if q len > 10 put ewa into q else
            # put inciscion box into q and save ewa
            # if no incision det, pop from q, if len of q = 0, no incision
            if len(frames[frames_ptr][names_to_labels['incision']]) > 0:
                incision_ewa_box = BETA * incision_ewa_box + (1 - BETA) *
                                    frames[frames_ptr][names_to_labels['incision']][0]
                if len(incision_q) > 10:
                    incision_q.append(incision_ewa_box)
                else:
                    incision_q.append(frames[frames_ptr][names_to_labels['incision']][0]['box'])
            else:
                # no incision detected, if q len > 0, pop q
                if len(incision_q) > 0:
                    incision_q.pop()
                else:
                    # q empty, reset ewa
                    if np.count_nonzero(incision_ewa_box):
                        incision_ewa_box = ewa_init_box.copy()
            continue

        # for each SI other than incision
        if len(frames[frames_ptr][si]) == 0:
            # no SI
            continue
        elif len(frames[frames_ptr][si]) == 1:
            if len(frames[frames_ptr - 1][si]) == 0:
                # if 1 si item in frame 1 but not in frame 0,
                # assign a new id
                frames[frames_ptr][si][0]['id'] = id_counter
                id_counter += 1
            elif len(frames[frames_ptr - 1][si]) == 1:
                # if only 1 of the same si item in both frames,
                # then they are the same si if within range
                vel =  calc_vel(frames[frames_ptr][si][0]['cen'], frames[frames_ptr - 1][si][0]['cen'])
                if abs(vel[0]) < MAX_VEL and abs(vel[1]) < MAX_VEL:
                    frames[frames_ptr][si][0]['id'] = frames[frames_ptr - 1][si][0]['id']
                    frames[frames_ptr][si][0]['link_id'] = frames[frames_ptr - 1][si][0]['link_id']
                    frames[frames_ptr][si][0]['link_cnt'] = frames[frames_ptr - 1][si][0]['link_cnt']
                    frames[frames_ptr][si][0]['vel-est'] = frames[frames_ptr - 1][si][0]['vel-act']
                    frames[frames_ptr][si][0]['vel-act'] = vel

                    frames[frames_ptr][si][0]['trk_cnt'] = frames[frames_ptr - 1][si][0]['trk_cnt'] + 1
                    # calc ewa
                    frames[frames_ptr][si][0]['box_ewa'] = BETA * frames[frames_ptr - 1][si][0]['box_ewa'] +
                                                        (1 - BETA) * frames[frames_ptr][si][0]['box']
                else:
                    # new SI
                    frames[frames_ptr][si][0]['id'] = id_counter
                    id_counter += 1
        else:
            # more than 1 of same SI's in prev frame
            # find the matching SI in prev frame
            cur_set_ind, prev_set_ind = calc_min_dist(si)
            for cur_i, prev_i in zip(cur_set_ind, prev_set_ind):
                vel =  calc_vel(frames[frames_ptr][si][cur_i]['cen'], frames[frames_ptr - 1][si][prev_i]['cen'])
                if abs(vel[0]) < MAX_VEL and abs(vel[1]) < MAX_VEL:
                    frames[frames_ptr][si][cur_i]['id'] = frames[frames_ptr - 1][si][prev_i]['id']
                    frames[frames_ptr][si][cur_i]['link_id'] = frames[frames_ptr - 1][si][prev_i]['link_id']
                    frames[frames_ptr][si][cur_i]['link_cnt'] = frames[frames_ptr - 1][si][prev_i]['link_cnt']
                    frames[frames_ptr][si][cur_i]['vel-est'] = frames[frames_ptr - 1][si][prev_i]['vel-act']
                    frames[frames_ptr][si][cur_i]['vel-act'] = vel

                    frames[frames_ptr][si][0]['trk_cnt'] = frames[frames_ptr - 1][si][0]['trk_cnt'] + 1
                    # calc ewa
                    frames[frames_ptr][si][0]['box_ewa'] = BETA * frames[frames_ptr - 1][si][0]['box_ewa'] +
                                                        (1 - BETA) * frames[frames_ptr][si][0]['box']
                else:
                    # new SI
                    frames[frames_ptr][si][cur_i]['id'] = id_counter
                    id_counter += 1

        for si in [names_to_labels['forceps'], names_to_labels['clamp'], names_to_labels['scalpel'],
                    names_to_labels['needle holder'], names_to_labels['suckers'], names_to_labels['bovie']]:
            # for these SI's, link a grasping glove for better tracking
            if len(frames[frames_ptr][si]) > 0:
                # if forceps detected, find closest glove
                for i in range(len(frames[frames_ptr][si])):
                    # for each SI
                    glove = closest_glove(frames[frames_ptr][si][i])
                    g_ioa = calc_ioa(glove['box'], frames[frames_ptr][si][i]['box'])
                    if g_ioa > 0.1:
                        # SI in grasp of glove, link them if not, else inc cnt
                        if frames[frames_ptr][si][i]['link_id'] == -1 or
                                frames[frames_ptr][si][i]['link_id'] !=  glove['link_id']:
                            frames[frames_ptr][si][i]['link_id'] = glove['link_id']
                            frames[frames_ptr][si][i]['link_cnt'] = 1
                        else:
                            frames[frames_ptr][si][i]['link_cnt'] += 1

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
