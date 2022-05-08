from imutils import paths
import face_recognition
import argparse
import pickle
import cv2
import os
import logging


logging.basicConfig(format='%(asctime)s [%(process)d] %(levelname)s : %(message)s', level=logging.INFO, datefmt='%m-%d-%Y %I:%M:%S %p')


args = argparse.ArgumentParser()
args.add_argument(
    "-i", "--dataset", required=True, help="path to input directory of faces + images"
)
args.add_argument(
    "-e", "--encodings", required=True, help="path to serialized db of facial encodings"
)

args.add_argument(
    "-d",
    "--detection-method",
    type=str,
    default="hog",
    help="face detection model to use: either `hog` or `cnn`",
)
args = vars(args.parse_args())

logging.info("Quantifying faces...")
image_paths = list(paths.list_images(args["dataset"]))

known_encodings = []
known_names = []

for (i, image_path) in enumerate(image_paths):
    logging.info("Processing image {}/{}".format(i + 1, len(image_paths)))
    name = image_path.split(os.path.sep)[-2]

    image = cv2.imread(image_path)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    boxes = face_recognition.face_locations(rgb, model=args["detection_method"])
    encodings = face_recognition.face_encodings(rgb, boxes)

    for encoding in encodings:
        known_encodings.append(encoding)
        known_names.append(name)


logging.info("Serializing encodings...")
data = {"encodings": known_encodings, "names": known_names}
f = open(args["encodings"], "wb")
f.write(pickle.dumps(data))
f.close()