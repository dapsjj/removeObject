import os
import cv2
import sys
import numpy as np


imgSet= "obj_remove"
file_list = os.listdir(imgSet)
file_list = [f for f in file_list if '.jpg' in f]
len_file_list = len(file_list)
def getHstMax(img, x, y):
    hist = np.zeros(256, dtype=np.uint8)
    for i in range(len_file_list):
        hist[img[i][x][y]] += 1
    return np.argmax(hist, 0)

def dealImg():
    img_width = 500
    img_height = 300
    imgsrc_list_y = []
    imgsrc_list_cr = []
    imgsrc_list_cb = []
    imgDst = np.zeros((img_height, img_width, 3), dtype=np.uint8)
    for f in file_list:
        img = cv2.imread(imgSet + os.sep + f)
        img_resize = cv2.resize(img, (img_width, img_height))
        imgYcc = cv2.cvtColor(img_resize, cv2.COLOR_BGR2YCR_CB)
        img_y = imgYcc[:, :, 0]
        img_cr = imgYcc[:, :, 1]
        img_cb = imgYcc[:, :, 2]
        imgsrc_list_y.extend([img_y])
        imgsrc_list_cr.extend([img_cr])
        imgsrc_list_cb.extend([img_cb])
    pix_arr_y = np.array(imgsrc_list_y)
    pix_arr_cr = np.array(imgsrc_list_cr)
    pix_arr_cb = np.array(imgsrc_list_cb)

    for y_position in range(img_height):
        for x_position in range(img_width):
            pix_y = getHstMax(pix_arr_y, y_position, x_position)
            pix_cr = getHstMax(pix_arr_cr, y_position, x_position)
            pix_cb = getHstMax(pix_arr_cb, y_position, x_position)
            imgDst[y_position, x_position, 0] = pix_y
            imgDst[y_position, x_position, 1] = pix_cr
            imgDst[y_position, x_position, 2] = pix_cb

    imgDst = cv2.cvtColor(imgDst, cv2.COLOR_YCR_CB2BGR)
    cv2.imwrite('hist_img.jpg', imgDst)
    print('done')


if __name__ == '__main__':
    dealImg()


