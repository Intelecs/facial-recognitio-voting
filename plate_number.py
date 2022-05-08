from distutils.log import debug

import pytesseract
from pytesseract import Output
from skimage.segmentation import clear_border
import numpy as np
import imutils
import cv2
from dataclasses import dataclass
import argparse
from imutils import paths
import time


@dataclass
class PlateNumberDetector:
    min_ar: int = 4
    max_ar: int = 5
    debug: bool = False
    engine: str = None

    def debug_image(self, title: str, image, wait: bool = True) -> None:
        if self.debug:
            cv2.imshow(title, image)

            if wait:
                cv2.waitKey(0)
        
    def plates_locations(self, gray: np.ndarray, keep=5) -> imutils.grab_contours:

        structure_element = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 5))
        blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, structure_element)
        
        if self.debug:
            self.debug_image("Debug", blackhat)
        
        light_strucutre = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        light = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, light_strucutre)
        light = cv2.threshold(light, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        if self.debug:
            self.debug_image("Debug", light)
        
        # Schar gradinet
        grad_x = cv2.Sobel(blackhat, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
        grad_x = np.absolute(grad_x)
        (min_val, max_val) = (np.min(grad_x), np.max(grad_x))
        grad_x = (255 * ((grad_x - min_val) / (max_val - min_val)))
        grad_x = grad_x.astype("uint8")

        if self.debug:
            self.debug_image("Debug", grad_x)

        grad_x =cv2.GaussianBlur(grad_x, (5, 5), 0)
        grad_x = cv2.morphologyEx(grad_x, cv2.MORPH_CLOSE, structure_element)
        threshold = cv2.threshold(grad_x, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        if self.debug:
            self.debug_image("Debug", threshold)
        
        threshold = cv2.erode(threshold, None, iterations=2)
        threshold = cv2.dilate(threshold, None, iterations=2)

        if self.debug:
            self.debug_image("Debug", threshold)
        
        threshold = cv2.bitwise_and(threshold, threshold, mask=light)
        threshold = cv2.dilate(threshold, None, iterations=2)
        threshold = cv2.erode(threshold, None, iterations=1)

        if self.debug:
            self.debug_image("Debug", threshold)
        
        contours = cv2.findContours(threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]

        return contours
    

    def license_plate(self, gray: np.ndarray, coordinates: imutils.grab_contours , _clear_border=False) -> tuple:

        license_plate_counter = None
        license_plate_roi = None

        for c in coordinates:
            (x, y, w, h) = cv2.boundingRect(c)
            ar = w / float(h)

            if ar >= self.min_ar or ar <= self.max_ar:

                license_plate_counter = c
                _license_plate = gray[y:y + h, x:x + w]
                license_plate_roi = cv2.threshold(_license_plate, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

                if _clear_border:
                    license_plate_roi = clear_border(license_plate_roi)

                if self.debug:
                    self.debug_image("ROI", license_plate_roi)
                    self.debug_image("PLATE", _license_plate)
                break
        
        return (license_plate_roi, license_plate_counter)
    
    def tessarct_options(self, psm: int = 7) -> str:
        alphanumeric = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

        options = "-c tessedit_char_whitelist={}".format(alphanumeric)
        options += " -psm {}".format(psm)

        return options
    
    def find_ocr(self, image: np.ndarray, psm: int = 7, _clear_border: bool =True) -> tuple:

        plate_text = None

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        coordinates = self.plates_locations(gray)
        (license_plate_roi, license_plate_counter) = self.license_plate(gray, coordinates, _clear_border)

        if plate_text is not None:
            options = self.tessarct_options(psm)
            plate_text = pytesseract.image_to_string(license_plate_roi, config=options)
            print(plate_text)

            if self.debug:
                self.debug_image("Debug", license_plate_roi)
        
        return (plate_text, license_plate_counter)



def clean_up(text: str) -> str:
    return "".join([c if ord(c) < 128 else "" for c in text]).strip()


args = argparse.ArgumentParser()
args.add_argument(
    '-i', "--input", required=True, help="input image"
)
args.add_argument(
    "-c", "--clear_border", type=int, help="clear border",default=-1
)
args.add_argument(
    "-p", "--psm", type=int, help="psm",default=7
)
args.add_argument(
    "-d", "--debug", help="debug", type=int, default=-1
)
args = vars(args.parse_args())

plateNumberDetector = PlateNumberDetector(debug=args["debug"] < 0)
image = args["input"]

image = cv2.imread(image)
image = imutils.resize(image, width=600)



(plate_text, contours) = plateNumberDetector.find_ocr(image, psm=args["psm"], _clear_border=args["clear_border"] < 0)

print(plate_text)