import os
import shutil
import glob

os.chdir("/home/kamiar/projects/opervu/images/labeled")
train_pre = "/home/kamiar/pCloudDrive/training/train_"
for i in range(5, 34):
    train_name = train_pre + str(i)
    files = glob.glob(train_name + '/*')
    for file in files:
        shutil.copy(file, '.')
