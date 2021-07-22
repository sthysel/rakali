import cv2 as cv

from .fps import cost
from .player import VideoPlayer
from .reader import VideoFile, VideoStream
from .writer import VideoWriter


def go(stopkey="q", wait=1):
    """
    Progress to next frame or quit on quit key
    """
    return cv.waitKey(wait) & 0xFF != ord(stopkey)
