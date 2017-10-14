#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import cv2

ROW_NUM = 480
COL_NUM = 640

# get histogram max
def get_hist_max(pix_arr, img_num):
    scale_num = 256
    hist = [0] * scale_num
    for img_counter in range(0, img_num):
        hist[pix_arr[img_counter]] += 1

    max_num = 0
    max_idx = -1
    for scale_counter in range(0, scale_num):
        if max_num < hist[scale_counter]:
            max_num = hist[scale_counter]
            max_idx = scale_counter

    return max_idx


def object_remove(dirpath,outputImgFile,outputcsv = None,dumpOn = False,dumpXY = None):
    file_arr = os.listdir(dirpath)
    # number of original images
    img_num = len(file_arr)

    channel_y = [0]*ROW_NUM
    channel_cr = [0]*ROW_NUM
    channel_cb = [0]*ROW_NUM

    img_result = np.zeros((ROW_NUM, COL_NUM, 3), dtype=np.uint8)

    # store pixels' info into channels
    for img_counter in range(0, img_num):
        filepath = dirpath + file_arr[img_counter]
        img = cv2.imread(filepath, 3)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)

        for row_counter in range(0, ROW_NUM):
            for col_counter in range(0, COL_NUM):
                if not isinstance(channel_y[row_counter], list):
                    channel_y[row_counter] = [0]*COL_NUM
                    channel_cr[row_counter] = [0]*COL_NUM
                    channel_cb[row_counter] = [0]*COL_NUM
                if not isinstance(channel_y[row_counter][col_counter], list):
                    channel_y[row_counter][col_counter] = [0]*img_num
                    channel_cr[row_counter][col_counter] = [0]*img_num
                    channel_cb[row_counter][col_counter] = [0]*img_num

                channel_y[row_counter][col_counter][img_counter] = img[row_counter, col_counter, 0]
                channel_cr[row_counter][col_counter][img_counter] = img[row_counter, col_counter, 1]
                channel_cb[row_counter][col_counter][img_counter] = img[row_counter, col_counter, 2]

    # calculating histogram max
    if dumpOn:
        print("---dump")
        csvFile = open(outputcsv, "w")
        print('img_counter,x,y,Y', file=csvFile)
        csvFile.close()
        dumpXYLen = len(dumpXY)
    for row_counter in range(0, ROW_NUM):
        for col_counter in range(0, COL_NUM):
            img_result[row_counter, col_counter, 0] = get_hist_max(channel_y[row_counter][col_counter], img_num)
            img_result[row_counter, col_counter, 1] = get_hist_max(channel_cr[row_counter][col_counter], img_num)
            img_result[row_counter, col_counter, 2] = get_hist_max(channel_cb[row_counter][col_counter], img_num)
            if dumpOn:
                for dumpXY_counter in range(0,dumpXYLen):
                    if dumpXY[dumpXY_counter][0] == col_counter and dumpXY[dumpXY_counter][1] == row_counter:
                        dump(col_counter, row_counter, channel_y, img_result)

    img_result = cv2.cvtColor(img_result, cv2.COLOR_YCrCb2BGR)
    cv2.imwrite(outputImgFile + os.sep +'hist_result.jpg', img_result)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
def dump(dumpX,dumpY,allValue,hist_max):
    csvFile = open(outputcsv, "a")
    for img_counter in range(0, len(allValue[dumpY][dumpX])):
        print("img_counter:%d,point:（%d,%d）,Y:%d"%(img_counter, dumpX, dumpY, allValue[dumpY][dumpX][img_counter]))
        print("%d,%d,%d,%d" % (img_counter, dumpX, dumpY, allValue[dumpY][dumpX][img_counter]),file=csvFile)

    print("hist_max point:（%d,%d）,Y:%d" % (dumpX, dumpY, hist_max[dumpY, dumpX, 0]))
    csvFile.close()

if __name__ == '__main__':
    dumpOn = True
    dumpXY = [[303,134],[122,41]]

    dirPath = 'obj_remove/'
    outputImgFile = './'
    outputcsv = 'debug.csv'

    object_remove(dirPath, outputImgFile, outputcsv, dumpOn, dumpXY)

