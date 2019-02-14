import cv2 as cv
import numpy as np
from pathlib import Path

import imutils


class Image:
    """OpenCV Image wrapper"""

    def __init__(self, image: np.array, copy=False):
        """construct from numpy array"""
        if copy:
            self.mat = image.copy()
        else:
            self.mat = image

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
        self.mat = imutils.translate(
            image=self.mat,
            x=x,
            y=y,
        )
        return self

    def rotate(self, angle, center=None, scale=1.0):
        """rotate image by given angle"""
        self.mat = imutils.rotate(
            image=self.mat,
            angle=angle,
            center=center,
            scale=scale,
        )
        return self

    def rotate_bound(self, angle):
        """rotate image by given angle"""

        self.mat = imutils.rotate_bound(
            image=self.mat,
            angle=angle,
        )
        return self

    def resize(self, width=None, height=None, interpolation=cv.INTER_AREA):
        """resise image preserving aspect ratio"""
        self.mat = imutils.resize(
            self.mat,
            width=None,
            height=None,
            inter=interpolation,
        )
        return self

    def skeletonize(self, size: int, structuring: int = cv.MORPH_RECT):
        """skeletonize image """
        self.mat = imutils.skeletonize(
            self.mat,
            size=size,
            structuring=structuring,
        )
        return self

    def bgr2rgb(self):
        """
        OpenCV represents images in BGR order. Other libraries like Matplotlib
        expects the image in RGB order
        """
        self.mat = cv.cvtColor(self.mat, cv.COLOR_BGR2RGB)
        return self

    def auto_canny(self, sigma=0.33):
        """compute the median of the single channel pixel intensities """
        self.mat = imutils.auto_canny(
            image=self.mat,
            sigma=sigma,
        )
        return self

    def adjust_brightness_contrast(self, brightness: float = 0.0, contrast: float = 0.0, beta=0):
        """
        Adjust the brightness and/or contrast of an image
        :param contrast: Float, contrast adjustment with 0 meaning no change
        :param brightness: Float, brightness adjustment with 0 meaning no change
        """

        self.mat = cv.addWeighted(
            src1=self.mat,
            alpha=1 + float(contrast) / 100.0,
            src2=self.mat,
            beta=beta,
            gamma=float(brightness),
        )
        return self

    def show(self, wait=0, key='q', name='Image'):
        """display image"""

        cv.imshow('Image', self.mat)
        if cv.waitKey(wait) & 0xFF == ord(key):
            return
