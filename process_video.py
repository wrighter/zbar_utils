#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import argparse
import time
from collections import defaultdict

import pyzbar.pyzbar as pyzbar
import numpy as np
import cv2 as cv


results = defaultdict(list)

def decode(im):
    # Find barcodes and QR codes
    decodedObjects = pyzbar.decode(im)

    # Print results
    # for obj in decodedObjects:
    #     print('Type : ', obj.type)
    #     print('Data : ', obj.data, '\n')

    return decodedObjects


def display(im, decodedObjects):
    # Loop over all decoded objects
    frame = im
    for decodedObject in decodedObjects:
        points = decodedObject.polygon

        # If the points do not form a quad, find convex hull
        if len(points) > 4:
            hull = cv.convexHull(np.array([point for point in points], dtype=np.float32))
            hull = list(map(tuple, np.squeeze(hull)))
        else:
            hull = points;

        # Number of points in the convex hull
        n = len(hull)
        #print(hull)
        # Draw the convext hull
        for j in range(0, n):
            if j == 0:
                try:
                    x= int(hull[j].x - 10)
                    y= int(hull[j].y - 10)
                except:
                    x= int(hull[j][0] - 10)
                    y= int(hull[j][1] - 10)
                print (decodedObject.data,x,y)
                cv.putText(frame,str(decodedObject.data),(x, y), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
            frame = cv.line(im, hull[j], hull[(j + 1) % n], (255, 0, 0), 3)
    return frame


def process(args):
    video = cv.VideoCapture(args.infile)

    if not video.isOpened():
        print("Could not open video")
        return

    basename = os.path.basename(args.infile)
    base = ''.join(basename.split('.')[0:-1])

    os.makedirs('video', exist_ok=True)

    if str(args.size) == "1080":
        shape=(1920, 1080)
    elif str(args.size) == "720":
        shape=(1280, 720)
    else:
        print('Unknown video size', args.size)
        sys.exit(1)
    # output in different formats
    out1 = cv.VideoWriter('./video/{}out.avi'.format(base),
                          cv.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30, shape)
    out2 = cv.VideoWriter('./video/{}out.mp4'.format(base),
                          cv.VideoWriter_fourcc(*'MP4V'), 30, shape)
    print('starting')
    counter = 0
    while True:
        # Read 2nd frame onwards
        ok, frame = video.read()
        if not ok:
            break

        print('frame ' + str(int(counter)))
        decodedObjects = decode(frame)
        ret_frame = display(frame, decodedObjects)
        cv.putText(ret_frame, "Frame no. : " + str(int(counter)), (100, 20), cv.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2);
        #Display result
        for obj in decodedObjects:
            results[obj.data].append(counter)
        out1.write(frame)
        out2.write(frame)
        counter += 1

    out1.release()
    out2.release()
    video.release()
    return counter

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('infile', help='Movie file to process')
    argparser.add_argument('--size', default=1080, help='Size (1080 or 720)')
    args = argparser.parse_args()

    start = time.time()
    frames = process(args)
    print('Found', len(results), ' barcodes')
    for code in sorted(results):
        print(code, 'found in ', len(results[code]), 'frames')

    print('Took ', time.time() - start, 'seconds to process', frames, 'frames')

if __name__ == '__main__':
    main()
