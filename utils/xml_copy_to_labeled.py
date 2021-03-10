#!/usr/bin/python3
import os
import glob
import shutil

for num in range(1, 34):
    path = '/home/kamiar/pCloudDrive/training/train_' + str(num)
    for fn in glob.glob(path + '/*.xml'):
        shutil.copy(fn,'/home/kamiar/projects/opervu/images/labeled')
