#!/usr/bin/python3

import os
import re
import glob
import collections

d = collections.defaultdict(int)

path = '/home/kamiar/projects/opervu/images/labeled'
for fn in glob.glob(path + '/*.xml'):

    with open(fn, 'r+') as f:
        cnt = f.read()
        labels = re.findall(r'(?<=<name>).*?(?=</name>)', cnt)
        if labels != None:
            for label in labels:
                d[label] += 1

ds = collections.OrderedDict(sorted(d.items(), key=lambda kv:kv[1], reverse=True))
for k in ds.keys():
    print(k)
