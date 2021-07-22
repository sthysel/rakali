import queue
import time
from threading import Thread

import cv2 as cv
import numpy as np
from rakali.video.fps import cost


class VideoFile:
    """
    Convenience interface to read video files
    """

    def __init__(self, src=0):
        self.stream = cv.VideoCapture(src)
        self.width = int(self.stream.get(cv.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.stream.get(cv.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.stream.get(cv.CAP_PROP_FPS)

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


class VideoStreamReader:
    """
    Reader of video streams
    - Arguments:
        - url_or_deviceid: (int or str) The url, filesystem path or id of the  video stream.
        - retries: (int) If there are errors reading the stream, how many times to retry.
    """

    def __init__(self, url_or_deviceid, retries=0):
        self._url_or_deviceid = url_or_deviceid
        self._video = None
        self._frame_count = 0
        self.retries = retries
        self._retries_count = 0

    def open(self):
        """
        Opens the video stream
        """
        if self._video is None:
            self._video = cv.VideoCapture(self._url_or_deviceid)

    def close(self):
        """
        Releases the video stream object
        """
        if self._video and self._video.isOpened():
            self._video.release()

    def next(self):
        """
        - Returns:
            - frame no / index  : integer value of the frame read
            - frame: np.array of shape (h, w, 3)

        - Raises:
            - StopIteration: after it finishes reading the video  file  \
                or if it reaches the number of retries without success.

        """

        while self._retries_count <= self.retries:
            if self._video.isOpened():
                success, frame = self._video.read()
                self._frame_count += 1
                if not success:
                    if self._video.isOpened():
                        self._video.release()
                    self._video = cv.VideoCapture(self._url_or_deviceid)
                else:
                    return (self._frame_count, frame)
            else:
                self._video = cv.VideoCapture(self._url_or_deviceid)
            self._retries_count += 1
        raise StopIteration()


class VideoStream(Thread):
    """
    Live video stream. This reader reads as fast as the stream can provide,
    overriding the previous frame.

    Use this when real-time processing is required
    """

    def __init__(
        self,
        src=0,
        name="video stream",
        fps=0,
    ):
        super().__init__()

        self.stream = cv.VideoCapture(self._pick_source(src))
        self.grabbed, self.frame = self.stream.read()
        self.stopped = False
        self.name = name

        # when reading from a file its sometimes useful to replay at a given
        # rate
        self._replay_delay = False
        if fps:
            self.fps = fps
            self._replay_delay = True
        else:
            self.fps = self.stream.get(cv.CAP_PROP_FPS)

        # ensure a frame is ready by faking it up, this saves a lot of ugly
        # fencing code later on
        self.width = int(self.stream.get(cv.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.stream.get(cv.CAP_PROP_FRAME_HEIGHT))
        self.frame = np.zeros((self.height, self.width, 3), np.uint8)

        self.frame_count = 0
        self.read_count = 0

    def dropped(self):
        """number of frames that was not read"""
        return self.frame_count - self.read_count

    def _pick_source(self, source):
        """
        click passes in source name as str, but usb vid cams are valid as well,
        and those are ints
        """
        if isinstance(source, int):
            return source
        elif isinstance(source, str):
            source = source.strip()
            if len(source) > 1:
                return source
            if len(source) == 1:
                try:
                    return int(source)
                except ValueError:
                    return source
            else:
                return source

    def size(self):
        return self.width, self.height

    def get_wh_size(self):
        """get width, height size of frame"""

        height, width = self.frame.shape[:2]
        return (width, height)

    def get_shape(self):
        return self.frame.shape

    def run(self):
        while not self.stopped:
            self.grabbed, self.frame = self.stream.read()
            self.frame_count += 1
            if self._replay_delay:
                time.sleep(1 / self.fps)

        self.stream.release()

    def read(self):
        """Return the latest frame """
        self.read_count += 1
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
        self.stopped = True
