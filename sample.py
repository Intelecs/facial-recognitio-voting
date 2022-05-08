import cv2
from vidgear.gears import CamGear
import math
import threading
import time
import dlib

car_model = cv2.CascadeClassifier('cars.xml')


def getCarsFromFrame(frame):
    result = car_model.detectMultiScale(frame, 1.15, 4)
    for (x, y, w, h) in result:
        cv2.rectangle(frame, (x, y), (x + w, y + h), color=(0, 255, 0), thickness=2)
    return frame



def detectCarsFromVideo():
    url = 'https://www.youtube.com/watch?v=Y1jTEyb3wiI' #https://www.youtube.com/watch?v=71zeC7LYqLE'
   # stream = CamGear(source=url, y_tube = True, logging=True).start() # YouTube Video URL as input
    stream = CamGear(source=url, stream_mode=True,
                     logging=True).start()  # YouTube Video URL as input

    while (True):
        frame = stream.read()
        controlkey = cv2.waitKey(1)
        if frame is not None:
            cars_frame = getCarsFromFrame(frame)
            cv2.imshow('frame', cars_frame)
        else:
            break
        if controlkey == ord('q'):
            break

    stream.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    detectCarsFromVideo()