import cv2 as cv
import numpy as np
from pathlib import Path

import imutils


class Image:
    """OpenCV Image wrapper"""

    def __init__(self, image: np.array, copy=False):
        """construct from numpy array"""
        if copy:
            self.image = image.copy()
        else:
            self.image = image

    @classmethod
    def fromfile(cls, path: Path):
        """load image from file"""
        img = cv.imread(path)
        return cls(img)

    @classmethod
    def fromurl(cls, url):
        """load image from url"""
        img = imutils.url_to_image(url)
        return cls(img)

    def translate(self, x: int, y: int):
        """translate image to given offsets"""
        return imutils.translate(
            image=self.image,
            x=x,
            y=y,
        )

    def rotate(self, angle, center=None, scale=1.0):
        """rotate image by given angle"""
        return imutils.rotate(
            image=self.image,
            angle=angle,
            center=center,
            scale=scale,
        )

    def rotate_bound(self, angle):
        """rotate image by given angle"""

        return imutils.rotate_bound(
            image=self.image,
            angle=angle,
        )

    def resize(self, width=None, height=None, interpolation=cv.INTER_AREA):
        """resise image preserving aspect ratio"""
        return imutils.resize(
            self.image,
            width=None,
            height=None,
            inter=interpolation,
        )

    def show(self, wait=0, key='q', name='Image'):
        """display image"""

        cv.imshow('Image', self.image)
        if cv.waitKey(wait) & 0xFF == ord(key):
            return
