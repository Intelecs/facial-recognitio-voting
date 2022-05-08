import numpy as np
from dataclasses import dataclass
from collections import OrderedDict
from scipy.spatial import distance as dist
from imutils.video import VideoStream, FileVideoStream
from imutils.io import TempFile
from imutils.video import FPS
from datetime import datetime
import imutils
import argparse
import dlib
import time 
import os
import json
import cv2
import logging

logging.basicConfig(format='%(asctime)s [%(process)d] %(levelname)s : %(message)s', level=logging.INFO, datefmt='%m-%d-%Y %I:%M:%S %p')


# @dataclass
# class CentroidTracker:

#     next_object_id: int = 0
#     objects = OrderedDict()
#     disappeared = OrderedDict()
#     bbox = OrderedDict()
#     max_disappeared: int = 30
#     max_distance: int = 0

#     def register(self, centroid, input_rect):
#         self.objects[self.next_object_id] = centroid
#         self.bbox[self.next_object_id] = input_rect
#         self.disappeared[self.next_object_id] = 0
#         self.next_object_id += 1

#     def degister(self, object_id: int):
#         del self.objects[object_id]
#         del self.disappeared[object_id]
#         del self.bbox[object_id]

#     def update(self, rects):
#         if len(rects) == 0:
#             for object_id in list(self.disappeared.keys()):
#                 self.disappeared[object_id] += 1
#                 if self.disappeared[object_id] > self.max_disappeared:
#                     self.degister(object_id)
#             return self.objects
#             # return self.bbox

#         input_centroids = np.zeros((len(rects), 2), dtype="int")
#         input_rects = []
#         for (i, (start_x, start_y, end_x, end_y)) in enumerate(rects):
#             c_x = int((start_x + end_x) / 2.0)
#             c_y = int((start_y + end_y) / 2.0)
#             input_centroids[i] = (c_x, c_y)
#             input_rects.append(rects[i])

#         if len(self.objects) == 0:
#             for i in range(0, len(input_centroids)):
#                 self.register(input_centroids[i], input_rects[i])
#         else:
#             object_ids = list(self.objects.keys())
#             object_centroids = list(self.objects.values())
#             D = dist.cdist(np.array(object_centroids), input_centroids)
#             rows = D.min(axis=1).argsort()
#             cols = D.argmin(axis=1)[rows]
#             used_rows = set()
#             used_cols = set()
#             for (row, col) in zip(rows, cols):
#                 if row in used_rows or col in used_cols:
#                     continue
                
#                 if D[row, col] > self.max_distance:
#                     continue

#                 object_id = object_ids[row]
#                 self.objects[object_id] = input_centroids[col]
#                 self.disappeared[object_id] = 0
#                 used_rows.add(row)
#                 used_cols.add(col)
#                 # if row not in used_rows or col not in used_cols: self.degister(object_id)

#             unused_rows = set(range(0, D.shape[0])).difference(used_rows)
#             unused_cols = set(range(0, D.shape[1])).difference(used_cols)
#             if D.shape[0] >= D.shape[1]:
#                 for row in unused_rows:
#                     object_id = object_ids[row]
#                     self.disappeared[object_id] += 1
#                     if self.disappeared[object_id] > self.max_disappeared:
#                         self.degister(object_id)
#             else:
#                 for col in unused_cols:
#                     self.register(input_centroids[col], input_rects[col])
#         return self.objects
#         # return self.bbox


@dataclass
class TrackableCars:

    object_id: str
    centroid = None
    centroids = None

    timestamp = {"A": 0, "B": 0, "C": 0, "D": 0}
    position = {"A": None, "B": None, "C": None, "D": None}
    last_point = False
    speed_mph = None
    speed_kmh = None

    estimated = False
    logged = None
    direction = None

    def calculate_speed(self, estimated_speeds: float):
        """
        Calculate the speed of the car in mph and kmh
        """
        self.speed_kmh = np.average(estimated_speeds)
        self.speed_mph = self.speed_kmh * 0.621371


args = argparse.ArgumentParser()
args.add_argument("-c", "--config", required=True, help="Path to the configuration file")
args = vars(args.parse_args())

config = None
with open(args["config"], "r") as f:
    config = json.load(f)
    f.close()


car_model = cv2.CascadeClassifier('cars.xml')

def get_cars_from_frame(frame):
    result = car_model.detectMultiScale(frame, 1.15, 4)
    for (x, y, w, h) in result:
        cv2.rectangle(frame, (x, y), (x + w, y + h), color=(0, 255, 0), thickness=2)
    return frame


net = cv2.dnn.readNetFromCaffe(config["prototxt_path"],
    config["model_path"])
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

height = None
width = None

centroid = CentroidTracker(
    max_disappeared=config["max_disapper"],
    max_distance=config["max_distance"]
)
trackers = []
trackable_objects = {}
total_frames = 0
points = [("A", "B"), ("B", "C"), ("C", "D")]

video_stream = FileVideoStream("sample.mp4").start()
time.sleep(1.0)

frames_per_second = FPS().start()

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
    "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
    "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
    "sofa", "train", "tvmonitor"]

while video_stream.running():

    frame = video_stream.read()
    timestamp = int(time.time())
    frame = imutils.resize(frame, width=config["frame_width"])
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    if width is None or height is None:
        (height, width) = frame.shape[:2]
        meters_per_pixel = config["distance"] / width
    
    rects = []

    if total_frames % config["track_objects"] == 0:
        
        trackers = []
        blob = cv2.dnn.blobFromImage(frame, size=(300, 300), ddepth=cv2.CV_8U)
        net.setInput(blob, scalefactor=1.0 / 127.5, mean=[127.5, 127.5, 127.5])
        detections = net.forward()
        for i in np.arange(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > config["confidence"]:
                idx = int(detections[0, 0, i, 1])

                if CLASSES[idx] != "car":
                    pass

                box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
                (start_x, start_y, end_x, end_y) = box.astype("int")

                tracker = dlib.correlation_tracker()
                rect = dlib.rectangle(start_x, start_y, end_x, end_y)
                tracker.start_track(rgb, rect)

                trackers.append(tracker)      
    else: 
        logging.info(f"Counting frames {trackers}")
        for tracker in trackers:
            tracker.update(rgb)
            pos = tracker.get_position()
            start_x = int(pos.left())
            start_y = int(pos.top())
            end_x = int(pos.right())
            end_y = int(pos.bottom())
            rects.append((start_x, start_y, end_x, end_y))
    
    objects = centroid.update(rects)

    for (object_id, centroid) in objects.items():

        to = trackable_objects.get(object_id, None)
        if to is None:
            to = TrackableCars(object_id)
            # trackable_objects[object_id] = to
        elif not to.estimated:
            if to.direction is None:
                y = [c[0] for c in to.centroids]
                direction = centroid[0] - np.mean(y)
                to.direction = direction
            if to.direction > 0:
                if to.timestamp["A"] == 0:
                    if centroid[0] > config["speed_estimation_zone"]["A"]:
                        to.timestamp["A"] = timestamp
                        to.position["A"] = centroid[0]
                elif to.timestamp["B"] == 0:
                    if centroid[0] > config["speed_estimation_zone"]["B"]:
                        to.timestamp["B"] = timestamp
                        to.position["B"] = centroid[0]
                elif to.timestamp["C"] == 0:
                    if centroid[0] > config["speed_estimation_zone"]["C"]:
                        to.timestamp["C"] = timestamp
                        to.position["C"] = centroid[0]
                elif to.timestamp["D"] == 0:
                    if centroid[0] > config["speed_estimation_zone"]["D"]:
                        to.timestamp["D"] = timestamp
                        to.position["D"] = centroid[0]

            elif to.direction < 0:
                if to.timestamp["D"] == 0:
                    if centroid[0] < config["speed_estimation_zone"]["D"]:
                        to.timestamp["D"] = timestamp
                        to.position["D"] = centroid[0]
                elif to.timestamp["C"] == 0:
                    if centroid[0] < config["speed_estimation_zone"]["C"]:
                        to.timestamp["C"] = timestamp
                        to.position["C"] = centroid[0]
                elif to.timestamp["B"] == 0:
                    if centroid[0] < config["speed_estimation_zone"]["B"]:
                        to.timestamp["B"] = timestamp
                        to.position["B"] = centroid[0]
                elif to.timestamp["A"] == 0:
                    if centroid[0] < config["speed_estimation_zone"]["A"]:
                        to.timestamp["A"] = timestamp
                        to.position["A"] = centroid[0]
            
            if to.last_point and not to.estimated:
                estimated_speeds = []

                for (i, j) in points:
                    _distance = to.position[j] - to.position[i]
                    distance_in_pixel = abs(_distance)

                    if distance_in_pixel == 0:
                        continue

                    _timestamp = to.timestamp[j] - to.timestamp[i]
                    time_in_seconds = abs(_timestamp.total_seconds())
                    time_in_hours = time_in_seconds / (60 * 60)

                    distance_in_meters = distance_in_pixel * meters_per_pixel
                    distance_in_km = distance_in_meters / 1000
                    estimated_speed = distance_in_km / time_in_hours
                    estimated_speeds.append(estimated_speed)
                
                to.calculate_speed(estimated_speeds)
                to.estimated = True
        trackable_objects[object_id] = to
        text = f"ID {object_id} - Speed: {to.speed_kmh} km/h"
        cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

    cv2.imshow("Frame", frame)
    cv2.waitKey(1)

    if video_stream.Q.qsize() < 2:
        time.sleep(0.001)
    total_frames += 1
    frames_per_second.update()




