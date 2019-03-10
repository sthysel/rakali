import cv2 as cv
import numpy as np
from pathlib import Path

from typing import Tuple

import imutils

from .annotate import add_frame_labels


class ImageSize:
    def __init__(
        self,
        height: int,
        width: int,
    ):
        self.height = height
        self.width = width

    def __call__(self):
        return (self.height, self.width)

    @classmethod
    def from_mat(cls, mat):
        height, width = mat.shape[:2]
        return cls(height, width)

    def __str__(self):
        return f'height: {self.height}, width: {self.width}'

    def __repr__(self):
        return f'ImageSize(height={self.height}, width={self.width})'


class Image:
    """OpenCV Image wrapper"""

    def __init__(self, image: np.array, copy=False):
        """construct from numpy array"""
        if copy:
            self.mat = image.copy()
        else:
            self.mat = image

    @classmethod
    def from_file(cls, path: Path):
        """load image from file"""
        img = cv.imread(path)
        return cls(img)

    @classmethod
    def from_url(cls, url):
        """load image from url"""
        img = imutils.url_to_image(url)
        return cls(img)

    def info(self):
        """print some information about the loaded image"""
        height, width, channels = self.mat.shape
        print(f'-- {width} px')
        print(f'|  {height} px')
        print(f'channels {channels}')

    def add_text(
        self,
        labels=[],
        **kwargs,
    ):
        """ Add labels to image"""
        add_frame_labels(frame=self.mat, labels=labels, **kwargs)

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

    def rotate_bounded(self, angle):
        """rotate image by given angle keeping withing origin image bounds"""

        self.mat = imutils.rotate_bound(
            image=self.mat,
            angle=angle,
        )
        return self

    def resize(self, width=None, height=None, interpolation=cv.INTER_AREA):
        """resise image preserving aspect ratio"""
        self.mat = imutils.resize(
            self.mat,
            width=width,
            height=height,
            inter=interpolation,
        )
        return self

    def scale(self, factor=1, interpolation=cv.INTER_AREA):
        """scale image"""

        self.mat = cv.resize(
            self.mat,
            None,
            fx=factor,
            fy=factor,
            interpolation=interpolation,
        )
        return self

    def grey(self):
        """Grey image """
        self.mat = cv.cvtColor(self.mat, cv.COLOR_BGR2GRAY)
        return self

    def gray(self):
        """Gray image """
        # irritating yanks
        return self.grey()

    def skeletonize(
        self,
        kernel_size: Tuple = (3, 3),
        structuring: int = cv.MORPH_RECT,
    ):
        """skeletonize image """

        grey = self.grey().mat

        # determine the area (i.e. total number of pixels in the image),
        # initialize the output skeletonized image, and construct the
        # morphological structuring element
        area = grey.shape[0] * grey.shape[1]
        skeleton = np.zeros(grey.shape, dtype="uint8")
        elem = cv.getStructuringElement(structuring, kernel_size)

        # erode and dilate the image using the structuring element
        eroded = cv.erode(grey, elem)
        temp = cv.dilate(eroded, elem)

        # subtract the temporary image from the original, eroded
        # image, then take the bitwise 'or' between the skeleton
        # and the temporary image
        temp = cv.subtract(grey, temp)
        skeleton = cv.bitwise_or(skeleton, temp)

        self.mat = skeleton

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
        while True:
            if cv.waitKey(wait) & 0xFF == ord(key):
                break

    def write(self, path):
        """write image to file"""
        cv.imwrite(filename=path, img=self.mat)
