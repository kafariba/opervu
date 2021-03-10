#!/usr/bin/python3
import os
import re
import glob

path = '/home/kamiar/projects/opervu/images/labeled'
os.chdir(path)
for fn in glob.glob('*.xml'):

    with open(fn, 'r+') as f:
        cnt = f.read()
        cnt = re.sub(r'esternal', r'sternal', cnt)
        cnt = re.sub(r'conector', r'connector', cnt)
        cnt = re.sub(r'rectractor', r'retractor', cnt)
        cnt = re.sub(r'cannual', r'cannula', cnt)
        cnt = re.sub(r'Snare', r'snare', cnt)
        cnt = re.sub(r'Glove', r'glove', cnt)
        cnt = re.sub(r'Clamp', r'clamp', cnt)
        cnt = re.sub(r'Sucker', r'sucker', cnt)
        cnt = re.sub(r'Forceps', r'forceps', cnt)
        cnt = re.sub(r'Obstraction', r'obstruction', cnt)
        cnt = re.sub(r'Venous Canula', r'venous cannula', cnt)
        cnt = re.sub(r'obstraction', r'obstruction', cnt)
        cnt = re.sub(r'Umbilical Tape', r'umbilical tape', cnt)
        cnt = re.sub(r'Pgw Stylet', r'pigtail drain', cnt)
        cnt = re.sub(r'pgw Stylet', r'pigtail drain', cnt)
        cnt = re.sub(r'3w Stopcock', r'3w stopcock', cnt)
        cnt = re.sub(r'nm sucker', r'arterial cannula', cnt)
        cnt = re.sub(r'Vesilloop', r'vesiloop', cnt)
        cnt = re.sub(r'Incision', r'incision', cnt)
        cnt = re.sub(r'Y\b', r'y', cnt)
        cnt = re.sub(r'BLack suture', r'black suture', cnt)
        cnt = re.sub(r'Introducer Sheath', r'introducer sheath', cnt)
        cnt = re.sub(r'cannla', r'cannula', cnt)
        cnt = re.sub(r'ROUND RETRACTOR', r'round retractor', cnt)
        cnt = re.sub(r'stopckock', r'stopcock', cnt)
        cnt = re.sub(r'holders', r'holder', cnt)
        cnt = re.sub(r'umilical', r'umbilical', cnt)
        cnt = re.sub(r'suter', r'suture', cnt)
        cnt = re.sub(r'forcepps', r'forceps', cnt)

    with open(fn, 'w') as f:
        f.write(cnt)
