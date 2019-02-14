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

    def skeletonize(self, size: int, structuring: int = cv.MORPH_RECT):
        """skeletonize image """
        return imutils.skeletonize(
            self.image,
            size=size,
            structuring=structuring,
        )

    def bgr2rgb(self):
        """
        OpenCV represents images in BGR order. Other libraries like Matplotlib
        expects the image in RGB order
        """
        return cv.cvtColor(self.image, cv.COLOR_BGR2RGB)

    def auto_canny(self, sigma=0.33):
        """compute the median of the single channel pixel intensities """
        return imutils.auto_canny(
            image=self.image,
            sigma=sigma,
        )

    def adjust_brightness_contrast(self, brightness: float = 0.0, contrast: float = 0.0, beta=0):
        """
        Adjust the brightness and/or contrast of an image
        :param contrast: Float, contrast adjustment with 0 meaning no change
        :param brightness: Float, brightness adjustment with 0 meaning no change
        """

        return cv.addWeighted(
            src1=self.image,
            alpha=1 + float(contrast) / 100.0,
            src2=self.image,
            beta=beta,
            gamma=float(brightness),
        )

    def show(self, wait=0, key='q', name='Image'):
        """display image"""

        cv.imshow('Image', self.image)
        if cv.waitKey(wait) & 0xFF == ord(key):
            return
