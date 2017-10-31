# coding: utf-8
from PIL import Image
import os
import cv2
import time
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True


# 横向拼接图片
def image_resize(img, size=(1200, 768)):#1920,1080
    try:
        if img.mode not in ('L', 'RGB'):
            img = img.convert('RGB')
        img = img.resize(size)
    except Exception:
        pass
    return img

def image_merge(images, restriction_max_width=None, restriction_max_height=None):
    """
    images - 要合并的图片路径列表
    ouput_dir - 输出路径
    output_name - 输出文件名
    restriction_max_width - 限制合并后的图片最大宽度，如果超过将等比缩小
    restriction_max_height - 限制合并后的图片最大高度，如果超过将等比缩小
    """
    global c3

    output_dir = r'D:/dealAfter/' + time.strftime('%Y-%m-%d')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    max_height = 0
    total_width = 0
    # 计算合成后图片的宽度（以最宽的为准）和高度
    for img_path in images:
        if os.path.exists(img_path):
            img = Image.open(img_path)
            width, height = img.size
            if height > max_height:
                max_height = height
            total_width += width

    # 产生一张空白图
    new_img = Image.new('RGB', (total_width, max_height), 255)
    # 合并
    x = y = 0
    for img_path in images:
        if os.path.exists(img_path):
            img = Image.open(img_path)
            width, height = img.size
            new_img.paste(img, (x, y))
            x += width

    if restriction_max_width and total_width >= restriction_max_width:
        # 如果宽度超过限制
        # 等比例缩小
        ratio = restriction_max_width / float(total_width)
        total_width = restriction_max_width
        max_height = int(max_height * ratio)
        new_img = image_resize(new_img, size=(total_width, max_height))

    if restriction_max_height and max_height >= restriction_max_height:
        # 如果高度超过限制
        # 等比例缩小
        ratio = restriction_max_height / float(max_height)
        total_width = int(total_width * ratio)
        max_height = restriction_max_height
        new_img = image_resize(new_img, size=(total_width, max_height))

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    save_path = '%s/%s' % (output_dir, '%04d' % c3 +'.jpg')
    c3 += 1
    new_img.save(save_path)

videoCapture1 = cv2.VideoCapture('VID_20171030_103458.mp4')
fps1 = videoCapture1.get(cv2.CAP_PROP_FPS)
fourcc1 = cv2.VideoWriter_fourcc(*'DIVX')
size1 = (640, 480)
c1 = 0

videoCapture2 = cv2.VideoCapture('VID_20171030_103458.mp4')
fps2 = videoCapture2.get(cv2.CAP_PROP_FPS)
fourcc2 = cv2.VideoWriter_fourcc(*'DIVX')
size2 = (640, 480)
c2 = 0
#
dir1 = r'D:/deal_pics1/' + time.strftime('%Y-%m-%d')
if not os.path.exists(dir1):
    os.makedirs(dir1)
#
dir2 = r'D:/deal_pics2/' + time.strftime('%Y-%m-%d')
if not os.path.exists(dir2):
    os.makedirs(dir2)

success1, frame1 = videoCapture1.read()
success2, frame2 = videoCapture2.read()
while success1 and success2:
    cv2.imwrite(dir1 + '/' + '%04d' % c1  + '.jpg', frame1)  # 保存

    c1 += 1
    success1, frame1 = videoCapture1.read()

    cv2.imwrite(dir2 + '/' + '%04d' % c2 + '.jpg', frame2)  # 保存
    c2 += 1
    success2, frame2 = videoCapture2.read()

dirs1 = os.listdir( dir1 )
dirs2 = os.listdir( dir2 )
c3 = 0
lendirs1 = len(dirs1)
lendirs2 = len(dirs2)
minlength = 0
minlength = lendirs1 if lendirs1 < lendirs2 else lendirs2
if minlength != 0:
    for cnt in range(minlength):
        a = dir1 + '/' + '%04d' % (cnt)+'.jpg'
        b = dir2 + '/' + '%04d' % (cnt)+'.jpg'
        image_merge(images=[a, b])


