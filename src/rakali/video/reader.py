from threading import Thread

import cv2 as cv
import numpy as np

from rakali.video.fps import cost

import queue


class VideoFile:
    """
    OpenCV has a tendency to present video streams from files at the recorded
    tempo, and this is generally useful until you need to post-process video at
    max speed, at which time it becomes a enormous PITA
    """

    def __init__(self, src=0):
        self.stream = cv.VideoCapture(src)
        self.width = int(self.stream.get(cv.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.stream.get(cv.CAP_PROP_FRAME_HEIGHT))

    def size(self):
        return self.width, self.height

    def get_wh_size(self):
        """get width, height size of frame"""

        height, width = self.frame.shape[:2]
        return (width, height)

    def get_shape(self):
        return self.frame.shape

    @cost
    def read(self):
        """Return the latest frame """
        return self.stream.read()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.stream.release()


class VideoFrameEnqueuer(Thread):
    """
    Loads images into a queue for processing by consumers.
    If a queue is not injected, create one.
    """

    def __init__(self, src=0, q=None):
        super().__init__()
        self.stopped = False
        if q is None:
            self.q = queue.Queue(maxsize=100)
        else:
            self.q = q

        self.stream = cv.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()

        self.width = int(self.stream.get(cv.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.stream.get(cv.CAP_PROP_FRAME_HEIGHT))

    def run(self):
        while not self.stopped:
            self.grabbed, self.frame = self.stream.read()
            count = int(self.stream.get(cv.CAP_PROP_POS_FRAMES))
            self.q.put((self.grabbed, self.frame, count))
        self.stream.release()

    def size(self):
        return self.width, self.height

    def get_wh_size(self):
        """get width, height size of frame"""

        height, width = self.frame.shape[:2]
        return (width, height)

    def get_shape(self):
        return self.frame.shape

    @cost
    def read(self):
        """Return the latest frame """
        return self.q.get(timeout=2)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stopped = True


class VideoStream:
    """
    Live video stream. This reader reads as fast as the stream can provide,
    overriding the previous frame.

    Use this when real-time processing is required
    """

    def __init__(self, src=0, name='video stream'):
        self.stream = cv.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False
        self.name = name

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
        while not self.stopped:
            self.grabbed, self.frame = self.stream.read()

    @cost
    def read(self):
        """Return the latest frame """
        return self.grabbed, self.frame

    def copy(self):
        """
        Return a copy of the latest frame. This is a safer way of retrieving
        frames, but also slightly slower.
        """
        return self.grabbed, np.copy(self.frame)

    def stop(self):
        self.stopped = True

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()
