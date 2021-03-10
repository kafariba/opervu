import os
import re
import glob
import sys

lbl = sys.argv[1]

lst = []
path = '/home/kamiar/projects/opervu/images/labeled'
for fn in glob.glob(path + '/*.xml'):

    with open(fn, 'r+') as f:
        cnt = f.read()
        m = re.search(lbl, cnt)
        if m != None:
            lst.append(fn)

lst.sort()
for f in lst:
    print(f)
