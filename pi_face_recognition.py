
from turtle import right
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
import logging

logging.basicConfig(format='%(asctime)s [%(process)d] %(levelname)s : %(message)s', level=logging.INFO, datefmt='%m-%d-%Y %I:%M:%S %p')

args = argparse.ArgumentParser()
args.add_argument(
    "-c", "--cascade", required=True, help="path to where the face cascade resides"
)
args.add_argument(
    "-e", "--encodings", required=True, help="path to serialized db of facial encodings"
)
args = vars(args.parse_args())

logging.info("Loading encodings + face detector...")
data = pickle.loads(open(args["encodings"], "rb").read())
detector = cv2.CascadeClassifier(args["cascade"])

logging.info("Starting video stream...")
video_stream = VideoStream(src=0).start()
time.sleep(2.0)

fps = FPS().start()

while True:
    frame = video_stream.read()
    frame = imutils.resize(frame, width=500)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    rects = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)

    boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

    encodings = face_recognition.face_encodings(rgb, boxes)
    names = []
    for encodings in encodings:
        matches = face_recognition.compare_faces(data['encodings'], encodings)
        name = "Unknown"

        if True in matches:
            matched_ids = [i for (i, b) in enumerate(matches) if b]
            counts = {}

            for i in matched_ids:
                name = data['names'][i]
                counts[name] = counts.get(name, 0) + 1
            
            name = max(counts, key=counts.get)
        names.append(name)
    
    for ((top, right, bottom, left), name) in zip(boxes, names):
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        # cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
        
        y = top - 15 if top - 15 > 15 else top + 15
        cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
    
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

fps.stop()
logging.info("Elasped time: {:.2f}".format(fps.elapsed()))
logging.info("Approx. FPS: {:.2f}".format(fps.fps()))
cv2.destroyAllWindows()
video_stream.stop()