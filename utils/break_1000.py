import os
import sys
import time
import shutil


dir_1 = '/home/kamiar/projects/opervu/images/surgery_images_9_18-1'
dir_2 = '/home/kamiar/projects/opervu/images/surgery_images_9_18-2'
dir_3 = '/home/kamiar/projects/opervu/images/surgery_images_9_18-3'
dest_pre = '/home/kamiar/projects/opervu/images/training/train_'

dir_num = 1
image_count = 0

image_list = sorted(os.listdir(dir_1))

for img in image_list:
    if image_count == 0 or image_count >= 1000:
        image_count = 1
        dir_num += 1
        os.makedirs(dest_pre + str(dir_num))
    else:
        image_count += 1
    shutil.move(os.path.join(dir_1, img), dest_pre + str(dir_num))

image_list = sorted(os.listdir(dir_2))

for img in image_list:
    if image_count == 0 or image_count >= 1000:
        image_count = 1
        dir_num += 1
        os.makedirs(dest_pre + str(dir_num))
    else:
        image_count += 1
    shutil.move(os.path.join(dir_2, img), dest_pre + str(dir_num))

image_list = sorted(os.listdir(dir_3))

for img in image_list:
    if image_count == 0 or image_count >= 1000:
        image_count = 1
        dir_num += 1
        os.makedirs(dest_pre + str(dir_num))
    else:
        image_count += 1
    shutil.move(os.path.join(dir_3, img), dest_pre + str(dir_num))
