#!/usr/bin/python3
import cv2
import os
import argparse
import sys

def video_to_frames(video, path_output_dir, imgnum):
    # extract frames from a video and save to directory as 'x.png' where
    # x is the frame index
    vidcap = cv2.VideoCapture(video)
    count = 1000
    vidcap.set(cv2.CAP_PROP_POS_MSEC,(count*1000))    # added this line
    while vidcap.isOpened():
        success, image = vidcap.read()
        if imgnum > 30:
            break
        if success:
            if imgnum < 16:
                count += 1
            else:
                count -= 1
            imgnum += 1
            cv2.imwrite(os.path.join(path_output_dir, '%d.jpg') % imgnum, image)
        else:
            break
    cv2.destroyAllWindows()
    vidcap.release()

def main(args=None):
    if args == None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser(description='Generate images from video.')
    parser.add_argument('vidname', help='name of video file')
    parser.add_argument('imgdir', help='dir path for images')
    parser.add_argument('imgnum', type=int, help='starting image number postfix')
    args = parser.parse_args(args)
    video_to_frames(args.vidname, args.imgdir, args.imgnum)

if __name__ == '__main__':
    args = ['/home/kamiar/Videos/opervu_videos/Children_Hosp_9-18/Surgery_2.avi', '/home/kamiar/projects/opervu/images/test/', '1']
    main(args)
