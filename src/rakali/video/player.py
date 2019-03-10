"""
Plays video
"""

import sys

import cv2 as cv
import imutils

from .reader import VideoStream


class VideoPlayer:
    """
    Plays videos
    """

    def __init__(self, stream: VideoStream, scale=1, window_name='Rakali Video'):
        """Video player"""

        self.stream = stream
        self.scale = scale
        self.window_name = window_name

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        cv.destroyAllWindows()

    def rescale(self, img):
        """Scale the resulting video display to better fit"""

        if self.scale != 1:
            return imutils.resize(img, width=int(img.shape[1] * self.resize))
        else:
            return img

    def play(self):
        with self.streams as st:
            while cv.waitKey(1) & 0xFF != ord('q'):
                img = self.rescale(st.read())
                cv.imshow(self.window_name, img)

        cv.destroyAllWindows()
        sys.exit()
