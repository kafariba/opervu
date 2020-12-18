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

#PATH_TO_VIDEO = '/home/kamiar/Videos/opervu_videos/Children_Hosp_9-18/Surgery_1.avi'
PATH_TO_VIDEO = '/home/kamiar/Videos/opervu_videos/Children_Hosp_9-18/cut1.avi'
# Open video file
vidcap = cv2.VideoCapture(PATH_TO_VIDEO)

count = 0

while(vidcap.isOpened()):
    # Acquire frame and expand frame dimensions to have shape: [1, None, None, 3]
    # i.e. a single-column array, where each item in the column has the pixel RGB value
    #vidcap.set(cv2.CAP_PROP_POS_MSEC,(count*10))
    success, image = vidcap.read()

    if success:
        count += 1
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

cv2.destroyAllWindows()
vidcap.release()
