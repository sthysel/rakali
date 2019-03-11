from threading import Thread

import cv2 as cv
import numpy as np


class VideoStream:
    """
    Live video stream. This reader reads as fast as the stream can provide,
    discarding the previous frame.
    """

    def __init__(self, src=0):
        self.stream = cv.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False

        # ensure a frame is ready by faking it up, this saves a lot of ugly
        # fencing code later on
        self.width = int(self.stream.get(cv.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.stream.get(cv.CAP_PROP_FRAME_HEIGHT))
        self.frame = np.zeros((self.height, self.width, 3), np.uint8)

    def size(self):
        return self.width, self.height

    def get_wh_size(self):
        """get width, height size of frame"""

        height, width = self.frame.shape[:2]
        return (width, height)

    def get_shape(self):
        return self.frame.shape

    def start(self):
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        while True:
            if self.stopped:
                return

            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        """Return the latest frame """
        return self.frame

    def copy(self):
        """
        Return a copy of the latest frame. This is a saver way of retrieving
        frames, but also slightly slower.
        """
        return np.copy(self.frame)

    def stop(self):
        self.stopped = True

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()
