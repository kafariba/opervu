import os
import shutil

os.chdir("/home/kamiar/projects/opervu/images/surgery_images_9_18-copy")
l = os.listdir()
for f in l:
    fn = os.path.splitext(f)[0].zfill(4)
    os.rename(f, fn + '.jpg')
