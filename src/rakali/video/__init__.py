import cv2 as cv
from .player import VideoPlayer
from .reader import VideoStream, VideoFile
from .writer import VideoWriter
from .fps import cost


def go(stopkey='q', wait=1):
    """
    Progress to nex frame or quit on quit key
    """
    return cv.waitKey(wait) & 0xFF != ord(stopkey)
