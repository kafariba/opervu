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
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='(%(lineno)s %(message)s',)


# set tf backend to allow memory to grow, instead of claiming everything
import tensorflow as tf

# The linear sum assignment problem is also known as minimum weight matching in bipartite graphs
#from scipy.optimize import linear_sum_assignment
from munkres import Munkres
my_munk = Munkres()

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
labels_to_names = {
0: 'forceps',
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
names_to_labels = {
'forceps': 0,
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

# use this label order to detect objects, address si dependency
si_track_order = [names_to_labels['obstruction'], names_to_labels['glove'], names_to_labels['bovie'], names_to_labels['incision'],
                   names_to_labels['forceps'], names_to_labels['clamp'], names_to_labels['scalpel'], names_to_labels['needle holder'],
                   names_to_labels['needle'], names_to_labels['sucker'], names_to_labels['sponge'], names_to_labels['gauze'],
                   names_to_labels['woods pack']]


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

# max si velocity
max_SI_vel = {0: [0,0],
1: [0,0],
2: [0,0],
3: [0,0],
4: [0,0],
5: [0,0],
6: [0,0],
7: [0,0],
8: [0,0],
9: [0,0],
10: [0,0],
11: [0,0],
12: [0,0]}

# init circulare frame cotainer
frames = []
frames_ptr = 0
prev_frames_ptr = 0
frame = {0:[], 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[], 9:[], 10:[], 11:[], 12:[]}
for i in range(10):
    frames.append(frame)

# init incision detection count, if > 10, draw it, else not
incision_det_count = 0

# flag to indicate obstruction of incision
incision_blocked = False

# create a numpy array of 100x4 and load it with nan for incision coordinates queue
tmp_lst = []
for i in range(100):
    tmp_lst.append([np.nan, np.nan, np.nan, np.nan])
incision_list = np.array(tmp_lst)

incision_list_ptr = 0

# SIs that are tracked
tracked_SIs = [names_to_labels['forceps'], names_to_labels['clamp'], names_to_labels['scalpel'],
            names_to_labels['needle'], names_to_labels['needle holder'], names_to_labels['sucker'],
            names_to_labels['gauze'], names_to_labels['bovie']]


# ID counter for tracked SI
id_counter = 0

# min num pixels for si to be considered moving
MIN_VEL = 5

# max num pixels that an instrument can travel from frame to frame
MAX_VEL = 250

# velocity offset for obstruction covering part of SI
ADJ_OBS_OFFSET = 150

# velocity offset for glove covering part of SI
ADJ_GLOVE_OFFSET = 50

# the vel delta for si in SI in grasp`
LINK_VEL_DELTA = 20

# keeps track of current frame number`
frameNumber = 0

# coeffs for exp wgt avg
BETA = 0.8
ONE_MINUS_BETA = 0.2

# lowest pix vals for bbox(x, y)
LOW_PIX = 30
HIGH_PIX = 2018

# center below/above these values are considered out of image
LOW_PIX_EDGE = 150
HIGH_PIX_EDGE = 1900

# newly detected SIs withing these edges are considered entering the image
LOW_PIX_ENTER = 350
HIGH_PIX_ENTER = 1700

#PATH_TO_VIDEO = '/home/kamiar/Videos/opervu_videos/Children_Hosp_9-18/Surgery_1.avi'
PATH_TO_VIDEO = '/home/kamiar/Videos/opervu_videos/Children_Hosp_9-18/test_1.avi'
# Open video file
vidcap = cv2.VideoCapture(PATH_TO_VIDEO)

def predict_first():
    global frames, frames_ptr, prev_frames_ptr, frameNumber

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

                frame[label].append({'id': -1, 'trk_cnt': 0, 'link_id': -1, 'link_cnt': 0, 'box':i_box,
                                        'scr':i_score, 'cen':i_center, 'cen_pred':[float('nan'), float('nan')],
                                        'vel':[0, 0], 'accel':[0, 0], 'adj_glove': -1, 'adj_obs': -1, 'in': '-', 'cov':0})

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
                prev_frames_ptr = 9
            else:
                prev_frames_ptr = frames_ptr - 1
            frames[frames_ptr] = frame

            # assign id/link id: correlate SIs from consecutive frames, link enclosing SIs (glove & forceps)
            track_SIs()

            pred_info = {'si':'', 'id':'', 'box':'', 'scr':'', 'cen':'', 'vel':'', 'misc':''}

            for si in frames[frames_ptr]:
                for si_item in frames[frames_ptr][si]:
                    pred_info['si'] += "{} {}/{}\n".format(labels_to_names[si], si_item['in'], si_item['cov'])
                    pred_info['id'] += "{}/{}\n".format(si_item['id'], si_item['trk_cnt'])
                    pred_info['box'] += "{:4d},{:4d},{:4d},{:4d}\n".format(si_item['box'][0],
                            si_item['box'][1], si_item['box'][2], si_item['box'][3])
                    pred_info['scr'] += "{:3d}\n".format(si_item['scr'])
                    pred_info['cen'] += "{},{}\n".format(si_item['cen'][0], si_item['cen'][1])
                    pred_info['vel'] += "{:.0f},{:.0f}/{:.0f},{:.0f}\n".format(si_item['vel'][0], si_item['vel'][1],
                                                                            si_item['accel'][0], si_item['accel'][1])
                    pred_info['misc'] += "{},{}/{}/{}/{}/{}\n".format(si_item['cen_pred'][0], si_item['cen_pred'][1],
                                            si_item['link_id'], si_item['link_cnt'], si_item['adj_glove'], si_item['adj_obs'])


            frames_ptr += 1
            frameNumber += 1
            return draw, pred_info, frameNumber
            # Press 'q' to quit
            #if cv2.waitKey(1) == ord('q'):
                #break

def box_center(box):
    # returns the center of the given rect. box
    return [int(round((box[0] + box[2]) / 2)), int(round((box[1] + box[3]) / 2))]

def calc_vel(si, box1, box2):
    global max_SI_vel
    # returns velocity of SI, center diff
    if box1[0] < LOW_PIX and box1[1] < LOW_PIX and box1[2] < HIGH_PIX and box1[3] < HIGH_PIX:
        cen1 = [box1[2], box1[3]]
        cen2 = [box2[2], box2[3]]
    elif box1[0] > LOW_PIX and box1[1] < LOW_PIX and box1[2] < HIGH_PIX and box1[3] < HIGH_PIX:
        cen1 = [int((box1[0] + box1[2])/2), box1[3]]
        cen2 = [int((box2[0] + box2[2])/2), box2[3]]
    elif box1[0] > LOW_PIX and box1[1] < LOW_PIX and box1[2] > HIGH_PIX and box1[3] < HIGH_PIX:
        cen1 = [box1[0], box1[3]]
        cen2 = [box2[0], box2[3]]
    elif box1[0] > LOW_PIX and box1[1] > LOW_PIX and box1[2] > HIGH_PIX and box1[3] < HIGH_PIX :
        cen1 = [box1[0], int((box1[1] + box1[3])/2)]
        cen2 = [box2[0], int((box2[1] + box2[3])/2)]
    elif box1[0] > LOW_PIX and box1[1] > LOW_PIX and box1[2] > HIGH_PIX and box1[3] > HIGH_PIX:
        cen1 = [box1[0], box1[1]]
        cen2 = [box2[0], box2[1]]
    elif box1[0] > LOW_PIX and box1[1] > LOW_PIX and box1[2] < HIGH_PIX and box1[3] > HIGH_PIX:
        cen1 = [int((box1[0] + box1[2])/2), box1[1]]
        cen2 = [int((box2[0] + box2[2])/2), box2[1]]
    elif box1[0] < LOW_PIX and box1[1] > LOW_PIX and box1[2] < HIGH_PIX and box1[3] > HIGH_PIX:
        cen1 = [box1[2], box1[1]]
        cen2 = [box2[2], box2[1]]
    elif box1[0] < LOW_PIX and box1[1] > LOW_PIX and box1[2] < HIGH_PIX and box1[3] < HIGH_PIX :
        cen1 = [box1[2], int((box1[1] + box1[3])/2)]
        cen2 = [box2[2], int((box2[1] + box2[3])/2)]
    else:
        cen1 = [int((box1[0] + box1[2]) / 2), int((box1[1] + box1[3]) / 2)]
        cen2 = [int((box2[0] + box2[2]) / 2), int((box2[1] + box2[3]) / 2)]

    vel = [cen1[0] - cen2[0], cen1[1] - cen2[1]]

    if abs(vel[0]) > max_SI_vel[si][0]:
        max_SI_vel[si][0] = abs(vel[0])
        logging.debug("F#{}: New max vel: {},{} for {}".format(frameNumber, max_SI_vel[si][0], max_SI_vel[si][1],
                                                               labels_to_names[si]))
    if abs(vel[1]) > max_SI_vel[si][1]:
        logging.debug("F#{}: New max vel: {},{} for {}".format(frameNumber, max_SI_vel[si][0], max_SI_vel[si][1],
                                                               labels_to_names[si]))
        max_SI_vel[si][1] = abs(vel[1])

    return vel

def calc_dist(pt1, pt2):
    # retrun dist btw two points
    return (int(round(math.sqrt((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2))))

def calc_min_dist(si):
    global frames, frames_ptr, prev_frames_ptr, my_munk
    # return the SI set in the old frame that are closest the new frame

    cost_mtx = []
    for si_item_a in frames[frames_ptr][si]:
        cost_mtx_row = []
        for si_item_b in frames[prev_frames_ptr][si]:
            cost_mtx_row.append(calc_dist(si_item_a['cen'], si_item_b['cen']))
        cost_mtx.append(cost_mtx_row)
    return my_munk.compute(cost_mtx)

def closest_glove(si_item):
    glove_dist = []

    for i, glv in enumerate(frames[frames_ptr][names_to_labels['glove']]):
        glove_dist.append((calc_dist(si_item['cen'], glv['cen']), i))

    if len(glove_dist) == 0:
        return None
    dist, i = min(glove_dist)
    return i

def closest_obs(si_item):
    obs_dist = []

    for i, obs in enumerate(frames[frames_ptr][names_to_labels['obstruction']]):
        obs_dist.append((calc_dist(si_item['cen'], obs['cen']), i))

    if len(obs_dist) == 0:
        return None
    dist, i = min(obs_dist)
    return i


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

    #cal area of box a
    box_a_area = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])

    #cal iou
    return inter_area / box_a_area

def adj_glove(si, cur_item, prev_item, glove_items):
    ind = closest_glove(cur_item)
    if ind != None:
        g_ioa = calc_ioa(glove_items[ind]['box'], cur_item['box'])
        if g_ioa > 0:
            # si and glove overlap
            cur_item['adj_glove'] = glove_items[ind]['id']
            cur_item['link_id'] = glove_items[ind]['id']
            if si == names_to_labels['gauze']:
                return glove_items[ind]['vel']
            if cur_item['link_id'] == prev_item['link_id']:
                cur_item['link_cnt'] = prev_item['link_cnt']
            else:
                cur_item['link_cnt'] = 0
            # logging.debug('g_ioa:{} si:{} x-diff:{} y-diff:{} total:{}'.format(g_ioa, labels_to_names[si], cur_item['vel'][0] - glove_items[ind]['vel'][0], cur_item['vel'][1] - glove_items[ind]['vel'][1],
                                                                      # abs(cur_item['vel'][0] - glove_items[ind]['vel'][0]) + abs(cur_item['vel'][1] - glove_items[ind]['vel'][1])))
            if (abs(glove_items[ind]['vel'][0]) > MIN_VEL or abs(glove_items[ind]['vel'][1]) > MIN_VEL) and \
                (abs(cur_item['vel'][0] - glove_items[ind]['vel'][0]) + abs(cur_item['vel'][1] - glove_items[ind]['vel'][1])) < LINK_VEL_DELTA:
                    # glove moving and si vel and glove vel equal, then link them
                    if cur_item['link_id'] == prev_item['link_id']:
                        cur_item['link_cnt'] += 1
        else:
            # si and glove do not overlap
            cur_item['adj_glove'] = -1
            cur_item['link_id'] = -1
            cur_item['link_cnt'] = 0

def adj_obs(cur_item, obs_items):
    ind = closest_obs(cur_item)
    if ind != None:
        g_ioa = calc_ioa(obs_items[ind]['box'], cur_item['box'])
        if g_ioa > 0:
            # obs covering si
            cur_item['adj_obs'] = obs_items[ind]['id']
        else:
            cur_item['adj_obs'] = -1

def id_to_item(id, si_item):
    for i in range(len(si_item)):
        if si_item[i]['id'] == id:
            return si_item[i]
    else:
        logging.debug("F#{}: Bad ID for index: {}".format(frameNumber, id))
        return None

def create_SI_ghost(si, si_item):
    global frames, frames_ptr, prev_frames_ptr

    vel = [si_item['vel'][0] + si_item['accel'][0], si_item['vel'][1] + si_item['accel'][1]]

    if si_item['link_id'] != -1:
        # si toches a glove
        if si_item['link_cnt'] > 1:
            # SI linked to a glove = in grasp
            cur_glv_item = id_to_item(si_item['link_id'], frames[frames_ptr][names_to_labels['glove']])
            if cur_glv_item == None:
                # glove out of view, SI should be too
                return
            prev_glv_item = id_to_item(si_item['link_id'], frames[prev_frames_ptr][names_to_labels['glove']])
            if cur_glv_item['cov'] == 0:
                if prev_glv_item['cov'] > 0:
                    # covered glove seen/detected but linked si not, don't ghost SI
                    return
                else:
                    # glove was not covered but si was either not detected or was covered, set the velocity to glove vel
                    vel = cur_glv_item['vel']
        else:
            # si linked to glove but not in grasp
            vel = [0, 0]

    box = [si_item['box'][0] + vel[0], si_item['box'][1] + vel[1], si_item['box'][2] + vel[0], si_item['box'][3] + vel[1]]

    center = [int(round(si_item['cen'][0] + vel[0])), int(round(si_item['cen'][1] + vel[1]))]
    center_pred = [int(round(center[0] + vel[0])), int(round(center[1] + vel[1]))]

    if LOW_PIX_EDGE < center[0] < HIGH_PIX_EDGE and LOW_PIX_EDGE < center[1] < HIGH_PIX_EDGE:
        si_item['cov'] += 1
        frames[frames_ptr][si].append({'id': si_item['id'], 'trk_cnt': si_item['trk_cnt'],
                                        'link_id': si_item['link_id'], 'link_cnt': si_item['link_cnt'],
                                        'box':box, 'scr':si_item['scr'], 'cen':center,
                                        'cen_pred':center_pred, 'vel':vel, 'accel':si_item['accel'],
                                        'adj_glove': si_item['adj_glove'], 'adj_obs': si_item['adj_obs'], 'in': '-', 'cov': si_item['cov']})
        logging.debug("F#{}: ghost SI in image: si={}, id={}, center={}".format(frameNumber, labels_to_names[si], si_item['id'], center))
    else:
        logging.debug("F#{}: ghost SI at the edge: si={}, id={}, center={}".format(frameNumber, labels_to_names[si], si_item['id'], center))

def ewa(v, t):
    return [round((BETA * v[0]) + (ONE_MINUS_BETA * t[0]), 2), round((BETA * v[1]) + (ONE_MINUS_BETA * t[1]), 2)]

def track_SIs():
    global id_counter, frames, frames_ptr, incision_det_count, prev_frames_ptr, frameNumber
    vel_offset = 0

    if frameNumber == 0:
        # first time in tracking, init ID's incrementally from 0
        for si in frames[0].keys():
            for si_item in frames[0][si]:
                si_item['id'] = id_counter
                id_counter += 1
        return

    # start with assumpltion that incision not bloacked, then check
    incision_blocked = False

    for si in si_track_order:
        # skip incision & obstruction, not tracked
        if si == names_to_labels['incision']:
            continue

        # check for blockage of incision
        if incision_det_count == 10 and (si in [names_to_labels['obstruction'],
                                                names_to_labels['glove'],
                                                names_to_labels['gauze']):
            if len(frames[frames_ptr][si]) > 0:
                for obst in frames[frames_ptr][si]:
                    if calc_ioa(incision_box.tolist(), obst['box']) > 0.9:
                        incision_blocked = True

        si_len = len(frames[frames_ptr][si])
        # check for spurious si detection
        if si_len == 2:
            # if si within another si, probably bad detection
            if calc_ioa(frames[frames_ptr][si][0]['box'], frames[frames_ptr][si][1]['box']) > 0.8:
                frames[frames_ptr][si].pop(1)
            elif calc_ioa(frames[frames_ptr][si][1]['box'], frames[frames_ptr][si][0]['box']) > 0.8:
                frames[frames_ptr][si].pop(0)
        elif si_len >= 3:
            ioa_pair = []
            for i in range(si_len):
                for j in range(i+1, si_len):
                    ioa_val = calc_ioa(frames[frames_ptr][si][i]['box'], frames[frames_ptr][si][j]['box']) + \
                                calc_ioa(frames[frames_ptr][si][j]['box'], frames[frames_ptr][si][i]['box'])
                    if ioa_val > 1:
                        ioa_pair.append((i, j))
            if len(ioa_pair) == 2:
                if ioa_pair[0][0] in ioa_pair[1]:
                    frames[frames_ptr][si].pop(ioa_pair[0][0])
                else:
                    frames[frames_ptr][si].pop(ioa_pair[0][1])


        # for each SI other than incision
        if len(frames[frames_ptr][si]) == 0:
            # no SI detected, check for SI in prev frame
            if len(frames[prev_frames_ptr][si]) == 0:
                # no SI
                continue
            else:
                for si_item in frames[prev_frames_ptr][si]:
                    # for all the SIs in prev frame
                    if si_item['id'] != -1 and si_item['trk_cnt'] > 1:
                        # SI tracked for more than 1 frame, predict its ghost in new frame
                        create_SI_ghost(si, si_item)
                    else:
                        logging.debug("F#{}: Did not ghost bc si not tracked: {} {},{}".format(frameNumber, labels_to_names[si], si_item['cen'][0], si_item['cen'][1]))

        elif len(frames[frames_ptr][si]) == 1:
            vel_offset = MAX_VEL
            if len(frames[prev_frames_ptr][si]) == 0:
                if si in tracked_SIs + [names_to_labels['glove']]:
                    # detect whether si covered by obstruction
                    adj_obs(frames[frames_ptr][si][0], frames[frames_ptr][names_to_labels['obstruction']])

                # new SI, if in the enterance edge start tracking
                if frames[frames_ptr][si][0]['cen'][0] < LOW_PIX_ENTER or frames[frames_ptr][si][0]['cen'][0] > HIGH_PIX_ENTER or \
                        frames[frames_ptr][si][0]['cen'][1] < LOW_PIX_ENTER or frames[frames_ptr][si][0]['cen'][1] > HIGH_PIX_ENTER or \
                        frames[frames_ptr][si][0]['box'][0] < LOW_PIX or frames[frames_ptr][si][0]['box'][0] > HIGH_PIX or \
                        frames[frames_ptr][si][0]['box'][1] < LOW_PIX or frames[frames_ptr][si][0]['box'][1] > HIGH_PIX or \
                        frames[frames_ptr][si][0]['adj_obs'] != -1:
                    frames[frames_ptr][si][0]['id'] = id_counter
                    id_counter += 1
                else:
                    logging.debug("F#{}: New si ignored b/c not in edge: {} {},{}".format(frameNumber, labels_to_names[si], frames[frames_ptr][si][0]['cen'][0], frames[frames_ptr][si][0]['cen'][1]))
                    frames[frames_ptr][si].pop()
            elif len(frames[prev_frames_ptr][si]) == 1:
                # if only 1 of the same si item in both frames,
                # then they are the same si if within velocity range

                vel = calc_vel(si, frames[frames_ptr][si][0]['box'], frames[prev_frames_ptr][si][0]['box'])
                frames[frames_ptr][si][0]['vel'] = vel  # ewa(frames[prev_frames_ptr][si][0]['vel'], vel)
                frames[frames_ptr][si][0]['accel'] = [int(vel[0] - frames[prev_frames_ptr][si][0]['vel'][0] + frames[prev_frames_ptr][si][0]['accel'][0] / 2),
                                                        int(vel[1] - frames[prev_frames_ptr][si][0]['vel'][1] + frames[prev_frames_ptr][si][0]['accel'][1] / 2)]
                frames[frames_ptr][si][0]['cen_pred'] = [frames[frames_ptr][si][0]['cen'][0] + vel[0],
                                                         frames[frames_ptr][si][0]['cen'][1] + vel[1]]

                if si in tracked_SIs:
                    # detect whether si covered by glove or obstruction
                    adj_obs(frames[frames_ptr][si][0], frames[frames_ptr][names_to_labels['obstruction']])
                    adj_glove(si, frames[frames_ptr][si][0], frames[prev_frames_ptr][si][0],
                                              frames[frames_ptr][names_to_labels['glove']])

                    # if covered by glove and glove is moving, if the same velocity then si grasped by glove, else increase MAX_VEL threshold
                    if frames[prev_frames_ptr][si][0]['link_id'] != 1 and frames[prev_frames_ptr][si][0]['link_cnt'] == 0:
                        vel_offset += ADJ_GLOVE_OFFSET

                    # if covered by obstruction and obstruction is moving, increase MAX_VEL velocity threshold
                    if frames[prev_frames_ptr][si][0]['adj_obs'] != 1:
                        vel_offset += ADJ_OBS_OFFSET

                elif si == names_to_labels['glove']:
                    # detect whether glove covered by obstruction and return velocity
                    adj_obs(frames[frames_ptr][si][0], frames[frames_ptr][names_to_labels['obstruction']])

                    vel_offset = MAX_VEL

                    # if covered by obstruction and it is moving, increase MAX_VEL velocity threshold
                    if frames[prev_frames_ptr][si][0]['link_id'] != 1 and frames[prev_frames_ptr][si][0]['link_cnt'] == 0:
                        vel_offset += ADJ_GLOVE_OFFSET



                if abs(vel[0]) < vel_offset and abs(vel[1]) < vel_offset:
                    frames[frames_ptr][si][0]['id'] = frames[prev_frames_ptr][si][0]['id']
                    frames[frames_ptr][si][0]['trk_cnt'] = frames[prev_frames_ptr][si][0]['trk_cnt'] + 1
                else:
                    # new SI
                    logging.debug("F#{}: si in new image not tracked to old, > max vel: {} {},{}".format(frameNumber, labels_to_names[si], frames[frames_ptr][si][0]['cen'][0], frames[frames_ptr][si][0]['cen'][1]))

                    if frames[frames_ptr][si][0]['cen'][0] < LOW_PIX_ENTER or frames[frames_ptr][si][0]['cen'][0] > HIGH_PIX_ENTER or \
                            frames[frames_ptr][si][0]['cen'][1] < LOW_PIX_ENTER or frames[frames_ptr][si][0]['cen'][1] > HIGH_PIX_ENTER or \
                            frames[frames_ptr][si][0]['box'][0] < LOW_PIX or frames[frames_ptr][si][0]['box'][0] > HIGH_PIX or \
                            frames[frames_ptr][si][0]['box'][1] < LOW_PIX or frames[frames_ptr][si][0]['box'][1] > HIGH_PIX or \
                            frameNumber == 1 or frames[frames_ptr][si][0]['adj_obs'] != -1:
                        frames[frames_ptr][si][0]['id'] = id_counter
                        id_counter += 1
                    else:
                        logging.debug("F#{}: New si ignored b/c in edge: {} {},{}".format(frameNumber, labels_to_names[si], frames[frames_ptr][si][0]['cen'][0], frames[frames_ptr][si][0]['cen'][1]))
                        frames[frames_ptr][si].pop()

                    # if other SI was tracked, ghost it
                    if frames[prev_frames_ptr][si][0]['id'] != -1 and frames[prev_frames_ptr][si][0]['trk_cnt'] > 1:
                        # SI tracked for more than 1 frame, predict cen & cen_pred
                        create_SI_ghost(si, frames[prev_frames_ptr][si][0])
                    else:
                        logging.debug("F#{}: Did not ghost bc si not tracked: {} {},{}".format(frameNumber, labels_to_names[si], frames[prev_frames_ptr][si][0]['cen'][0], frames[prev_frames_ptr][si][0]['cen'][1]))

            else:
                # only 1 SI in cur frame, but more than 1 in prev
                indexes = calc_min_dist(si)
                for cur_i, prev_i in indexes:

                    vel_offset = MAX_VEL

                    vel =  calc_vel(si, frames[frames_ptr][si][cur_i]['box'], frames[prev_frames_ptr][si][prev_i]['box'])
                    frames[frames_ptr][si][cur_i]['vel'] = vel  # ewa(frames[prev_frames_ptr][si][0]['vel'], vel)
                    frames[frames_ptr][si][cur_i]['accel'] = [int(vel[0] - frames[prev_frames_ptr][si][prev_i]['vel'][0] + frames[prev_frames_ptr][si][prev_i]['accel'][0] / 2),
                                                            int(vel[1] - frames[prev_frames_ptr][si][prev_i]['vel'][1] + frames[prev_frames_ptr][si][prev_i]['accel'][1] / 2)]
                    frames[frames_ptr][si][cur_i]['cen_pred'] = [frames[frames_ptr][si][cur_i]['cen'][0] + vel[0],
                                                                frames[frames_ptr][si][cur_i]['cen'][1] + vel[1]]

                    if si in tracked_SIs:
                        # detect whether si covered by glove or obstruction
                        adj_obs(frames[frames_ptr][si][cur_i], frames[frames_ptr][names_to_labels['obstruction']])
                        adj_glove(si, frames[frames_ptr][si][cur_i], frames[prev_frames_ptr][si][prev_i],
                                                  frames[frames_ptr][names_to_labels['glove']])

                         # if covered by glove and glove is moving, if the same velocity then si grasped by glove, else increase MAX_VEL threshold
                        if frames[prev_frames_ptr][si][prev_i]['link_id'] != 1 and frames[prev_frames_ptr][si][prev_i]['link_cnt'] == 0:
                            vel_offset += ADJ_GLOVE_OFFSET

                        # if covered by obstruction and obstruction is moving, increase MAX_VEL threshold
                        if frames[prev_frames_ptr][si][prev_i]['adj_obs'] != 1:
                            vel_offset += ADJ_OBS_OFFSET


                    elif si == names_to_labels['glove']:
                        # detect whether glove covered by obstruction
                        adj_obs(frames[frames_ptr][si][cur_i], frames[frames_ptr][names_to_labels['obstruction']])

                        # if covered by obstruction and obstruction is moving, increase MAX_VEL threshold
                        if frames[prev_frames_ptr][si][prev_i]['link_id'] != 1 and frames[prev_frames_ptr][si][prev_i]['link_cnt'] == 0:
                            vel_offset += ADJ_GLOVE_OFFSET

                    if abs(vel[0]) < vel_offset and abs(vel[1]) < vel_offset:
                        frames[frames_ptr][si][cur_i]['id'] = frames[prev_frames_ptr][si][prev_i]['id']
                        frames[frames_ptr][si][cur_i]['trk_cnt'] = frames[prev_frames_ptr][si][prev_i]['trk_cnt'] + 1
                    else:
                        # new SI
                        logging.debug("F#{}: si in new image not tracked to old, > max vel: {} {},{}".format(frameNumber, labels_to_names[si], frames[frames_ptr][si][cur_i]['cen'][0], frames[frames_ptr][si][cur_i]['cen'][1]))
                        if frames[frames_ptr][si][cur_i]['cen'][0] < LOW_PIX_ENTER or frames[frames_ptr][si][cur_i]['cen'][0] > HIGH_PIX_ENTER or \
                                frames[frames_ptr][si][cur_i]['cen'][1] < LOW_PIX_ENTER or frames[frames_ptr][si][cur_i]['cen'][1] > HIGH_PIX_ENTER or \
                                frames[frames_ptr][si][cur_i]['box'][0] < LOW_PIX or frames[frames_ptr][si][cur_i]['box'][0] > HIGH_PIX or \
                                frames[frames_ptr][si][cur_i]['box'][1] < LOW_PIX or frames[frames_ptr][si][cur_i]['box'][1] > HIGH_PIX or \
                                frameNumber == 1 or frames[frames_ptr][si][cur_i]['adj_obs'] != -1:
                            frames[frames_ptr][si][cur_i]['id'] = id_counter
                            id_counter += 1
                        else:
                            logging.debug("F#{}: New si ignored b/c in edge: {} {},{}".format(frameNumber, labels_to_names[si], frames[frames_ptr][si][cur_i]['cen'][0], frames[frames_ptr][si][cur_i]['cen'][1]))
                            frames[frames_ptr][si].pop(cur_i)
                        # if other SI was tracked, ghost it
                        if frames[prev_frames_ptr][si][prev_i]['id'] != -1 and frames[prev_frames_ptr][si][prev_i]['trk_cnt'] > 1:
                            # SI tracked for more than 1 frame, predict cen & cen_pred
                            create_SI_ghost(si, frames[prev_frames_ptr][si][prev_i])
                        else:
                            logging.debug("F#{}: Did not ghost bc si not tracked: {} {},{}".format(frameNumber, labels_to_names[si], frames[prev_frames_ptr][si][prev_i]['cen'][0], frames[prev_frames_ptr][si][prev_i]['cen'][1]))

                for i in range(len(frames[prev_frames_ptr][si])):
                    # for all the SIs in prev frame that were not match with cur frame
                    for j in range(len(indexes)):
                        if i == indexes[j][1]:
                            break
                    else:
                        # SI in prev frame that were not matched
                        if frames[prev_frames_ptr][si][i]['id'] != -1 and frames[prev_frames_ptr][si][i]['trk_cnt'] > 1:
                            # SI tracked for more than 1 frame, predict cen & cen_pred
                            create_SI_ghost(si, frames[prev_frames_ptr][si][i])

        else:
            # more than 1 SI in cur frame

            # find the matching SI in prev frame
            items_to_pop = []
            indexes = calc_min_dist(si)
            for cur_i, prev_i in indexes:

                vel_offset = MAX_VEL

                vel =  calc_vel(si, frames[frames_ptr][si][cur_i]['box'], frames[prev_frames_ptr][si][prev_i]['box'])
                frames[frames_ptr][si][cur_i]['vel'] = vel  # ewa(frames[prev_frames_ptr][si][0]['vel'], vel)
                frames[frames_ptr][si][cur_i]['accel'] = [int(vel[0] - frames[prev_frames_ptr][si][prev_i]['vel'][0] + frames[prev_frames_ptr][si][prev_i]['accel'][0] / 2),
                                                            int(vel[1] - frames[prev_frames_ptr][si][prev_i]['vel'][1] + frames[prev_frames_ptr][si][prev_i]['accel'][1] / 2)]
                frames[frames_ptr][si][cur_i]['cen_pred'] = [frames[frames_ptr][si][cur_i]['cen'][0] + vel[0],
                                                         frames[frames_ptr][si][cur_i]['cen'][1] + vel[1]]

                if si in tracked_SIs:
                    # detect whether si covered by glove or obstruction
                    adj_obs(frames[frames_ptr][si][cur_i], frames[frames_ptr][names_to_labels['obstruction']])
                    adj_glove(si, frames[frames_ptr][si][cur_i], frames[prev_frames_ptr][si][prev_i],
                                              frames[frames_ptr][names_to_labels['glove']])

                    # if covered by glove and glove is moving, if the same velocity then si grasped by glove, else increase MAX_VEL threshold
                    if frames[prev_frames_ptr][si][prev_i]['link_id'] != 1 and frames[prev_frames_ptr][si][prev_i]['link_cnt'] == 0:
                        vel_offset += ADJ_GLOVE_OFFSET

                    # if covered by obstruction and obstruction is moving, increase MAX_VEL threshold
                    if frames[prev_frames_ptr][si][prev_i]['adj_obs'] != 1:
                        vel_offset += ADJ_OBS_OFFSET


                elif si == names_to_labels['glove']:
                    # detect whether glove covered by obstruction
                    adj_obs(frames[frames_ptr][si][cur_i], frames[frames_ptr][names_to_labels['obstruction']])

                    # if covered by obstruction and obstruction is moving, increase MAX_VEL threshold
                    if frames[prev_frames_ptr][si][prev_i]['link_id'] != 1 and frames[prev_frames_ptr][si][prev_i]['link_cnt'] == 0:
                        vel_offset += ADJ_GLOVE_OFFSET

                if abs(vel[0]) < vel_offset and abs(vel[1]) < vel_offset:
                    frames[frames_ptr][si][cur_i]['id'] = frames[prev_frames_ptr][si][prev_i]['id']
                    frames[frames_ptr][si][cur_i]['trk_cnt'] = frames[prev_frames_ptr][si][prev_i]['trk_cnt'] + 1
                else:
                    # new SI
                    logging.debug("F#{}: si in new image not tracked to old, > max vel: {} {},{}".format(frameNumber, labels_to_names[si], frames[frames_ptr][si][cur_i]['cen'][0], frames[frames_ptr][si][cur_i]['cen'][1]))
                    if frames[frames_ptr][si][cur_i]['cen'][0] < LOW_PIX_ENTER or frames[frames_ptr][si][cur_i]['cen'][0] > HIGH_PIX_ENTER or \
                            frames[frames_ptr][si][cur_i]['cen'][1] < LOW_PIX_ENTER or frames[frames_ptr][si][cur_i]['cen'][1] > HIGH_PIX_ENTER or \
                            frames[frames_ptr][si][cur_i]['box'][0] < LOW_PIX or frames[frames_ptr][si][cur_i]['box'][0] > HIGH_PIX or \
                            frames[frames_ptr][si][cur_i]['box'][1] < LOW_PIX or frames[frames_ptr][si][cur_i]['box'][1] > HIGH_PIX or \
                            frameNumber == 1 or frames[frames_ptr][si][cur_i]['adj_obs'] != -1:
                        frames[frames_ptr][si][cur_i]['id'] = id_counter
                        id_counter += 1
                    else:
                        logging.debug("F#{}: New si ignored b/c did come from the edge: {} {},{}".format(frameNumber, labels_to_names[si], frames[frames_ptr][si][cur_i]['cen'][0], frames[frames_ptr][si][cur_i]['cen'][1]))
                        items_to_pop.append(cur_i)
                    # if other SI was tracked, ghost it
                    if frames[prev_frames_ptr][si][prev_i]['id'] != -1 and frames[prev_frames_ptr][si][prev_i]['trk_cnt'] > 1:
                        # SI tracked for more than 1 frame, predict cen & cen_pred
                        create_SI_ghost(si, frames[prev_frames_ptr][si][prev_i])
                    else:
                        logging.debug("F#{}: Did not ghost bc si not tracked: {} {},{}".format(frameNumber, labels_to_names[si], frames[prev_frames_ptr][si][prev_i]['cen'][0], frames[prev_frames_ptr][si][prev_i]['cen'][1]))

            vel_offset = MAX_VEL

            for i in range(len(frames[frames_ptr][si])):
                    # for all the SIs in cur frame that were not match with prev frame
                    for j in range(len(indexes)):
                        if i == indexes[j][0]:
                            break
                    else:
                        if si in tracked_SIs + [names_to_labels['glove']]:
                            # detect whether si covered by obstruction
                            adj_obs(frames[frames_ptr][si][i], frames[frames_ptr][names_to_labels['obstruction']])

                        if frames[frames_ptr][si][i]['cen'][0] < LOW_PIX_ENTER or frames[frames_ptr][si][i]['cen'][0] > HIGH_PIX_ENTER or \
                                frames[frames_ptr][si][i]['cen'][1] < LOW_PIX_ENTER or frames[frames_ptr][si][i]['cen'][1] > HIGH_PIX_ENTER or \
                                frames[frames_ptr][si][cur_i]['box'][0] < LOW_PIX or frames[frames_ptr][si][cur_i]['box'][0] > HIGH_PIX or \
                                frames[frames_ptr][si][cur_i]['box'][1] < LOW_PIX or frames[frames_ptr][si][cur_i]['box'][1] > HIGH_PIX or \
                                frameNumber == 1 or frames[frames_ptr][si][i]['adj_obs'] != -1:
                            frames[frames_ptr][si][i]['id'] = id_counter
                            id_counter += 1
                        else:
                            logging.debug("====>>>> F#{}: New si ignored, cen NOT in the edge: {} {},{}".format(frameNumber, labels_to_names[si], frames[frames_ptr][si][i]['cen'][0], frames[frames_ptr][si][i]['cen'][1]))
                            items_to_pop.append(i)

            for i in range(len(frames[prev_frames_ptr][si])):
                # for all the SIs in prev frame that were not match with cur frame
                for j in range(len(indexes)):
                    if i == indexes[j][1]:
                        break
                else:
                    # SI in prev frame that were not matched
                    if frames[prev_frames_ptr][si][i]['id'] != -1 and frames[prev_frames_ptr][si][i]['trk_cnt'] > 1:
                        # SI tracked for more than 1 frame, predict cen & cen_pred
                        create_SI_ghost(si, frames[prev_frames_ptr][si][i])
                    else:
                        logging.debug("F#{}: Did not ghost bc si not tracked: {} {},{}".format(frameNumber, labels_to_names[si], frames[prev_frames_ptr][si][i]['cen'][0], frames[prev_frames_ptr][si][i]['cen'][1]))

            items_to_pop.sort(reverse = True)
            for i in range(len(items_to_pop)):
                frames[frames_ptr][si].pop(items_to_pop[i])
            items_to_pop.clear()

    # do this after tracking to update imcision_box
    si = names_to_labels['incision']
    if len(frames[frames_ptr][si]) > 0:
        if incision_det_count < 10:
            incision_det_count += 1
        incision_list[incision_list_ptr] = (frames[frames_ptr][si][0]['box'])
        incision_list_ptr += 1
        if incision_list_ptr >= 100:
            incision_list_ptr = 0
        incision_box = np.nanmax(incision_list, axis=0)
        frames[frames_ptr][si][0]['box'] = incision_box.tolist()
    else:
        # no incision detected, if not blocked decrement count & update buf
        if not incision_blocked:
            if incision_det_count > 0:
                incision_det_count -= 1
            else:
                incision_list[incision_list_ptr] = [np.nan, np.nan, np.nan, np.nan]
                incision_list_ptr += 1
                if incision_list_ptr >= 100:
                    incision_list_ptr = 0
                incision_box = np.nanmax(incision_list, axis=0)
                if incision_box.max() != np.nan:
                    frames[frames_ptr][si][0]['box'] = incision_box.tolist()



def quit():
    cv2.destroyAllWindows()
    vidcap.release()
