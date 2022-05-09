#coding=utf-8
from cv2 import dnn
import cv2
import time
import numpy as np
import pytesseract
from PIL import Image
from pytesseract import Output

inWidth = 720
inHeight = 1024
WHRatio = inWidth / float(inHeight)
inScaleFactor = 0.007843
meanVal = 127.5

classNames = ('background',
              'plate')
net = dnn.readNetFromCaffe("tests.prototxt","lpr.caffemodel")



print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe("tests.prototxt", "lpr.caffemodel")
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

frame = cv2.imread("1.jpeg")
blob = cv2.dnn.blobFromImage(frame, size=(300, 300), ddepth=cv2.CV_8U)
net.setInput(blob, scalefactor=1.0/127.5, mean=[127.5,
            127.5, 127.5])

detections = net.forward()
inWidth = 720
inHeight = 1024
WHRatio = inWidth / float(inHeight)

cols = frame.shape[1]
rows = frame.shape[0]

if cols / float(rows) > WHRatio:
    cropSize = (int(rows * WHRatio), rows)
else:
    cropSize = (cols, int(cols / WHRatio))


for i in np.arange(0, detections.shape[2]):
    confidence = detections[0, 0, i, 2]

    if confidence > 0.2:
        idx = int(detections[0, 0, i, 1])

        xLeftBottom = int(detections[0, 0, i, 3] * cols) - 20
        yLeftBottom = int(detections[0, 0, i, 4] * rows) - 20
        xRightTop = int(detections[0, 0, i, 5] * cols) - 4
        yRightTop = int(detections[0, 0, i, 6] * rows)+ 20
        # cv2.rectangle(frame, (xLeftBottom, yLeftBottom), (xRightTop, yRightTop),
        #                   (0, 255, 255))

        # image[ystart:ystop, xstart:xstop]

        croped = frame[yLeftBottom:yRightTop, xLeftBottom:xRightTop]
        print(classNames[idx])

        gray = cv2.cvtColor(croped, cv2.COLOR_BGR2GRAY)
        # gray = cv2.resize(gray, (600, 600))
        cv2.imwrite("croped.jpeg", gray)

        image = Image.open("croped.jpeg")
        # image = gray
        image = np.array(image)
        norm_img = np.zeros((image.shape[0], image.shape[1]))
        image = cv2.normalize(image, norm_img, 0, 255, cv2.NORM_MINMAX)
        image = cv2.threshold(image, 100, 255, cv2.THRESH_BINARY)[1]
        image = cv2.GaussianBlur(image, (1, 1), 0)
        
        text = pytesseract.image_to_string(image)
        results = pytesseract.image_to_data(image, output_type=Output.DICT)
        
        plate_number = ""
        text = results['text']
        for i in range(len(text)):
            if text[i] != '':                
                plate_number += text[i].replace('\n', '').replace(' ', '').replace('-', '').replace('“', '')
        
        if len(plate_number) > 0:
            print(plate_number[1:len(plate_number)])
        cv2.imshow("Frame", image)
        
        cv2.waitKey(0)
