#!/usr/bin/python3

import os
import glob
import shutil

l_path = '/home/kamiar/projects/opervu/images/labeled'
for num in range(1, 34):
    r_path = '/home/kamiar/pCloudDrive/training/train_' + str(num)
    os.chdir(r_path)
    for fn in glob.glob('*.xml'):
        shutil.copy(os.path.join(l_path,fn), fn)
