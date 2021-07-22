"""
Rakali image processing
"""

advice = """
OpenCV needs to be installed.
Many users use opencv-cuda or some custom OpenCV built and do not appreciate that
being clobbered.

For standard usuage just install from pip:
$ pip install opencv-python

For arch-linux use the opencv-cuda pac from AUR:
$ yay -S opencv-cuda
"""

import sys

try:
    import cv2
except ImportError:
    print(advice)
    sys.exit()

version = "0.0.10"

from .img import Image, ImageSize
from .video.player import VideoPlayer
from .video.reader import VideoStream
from .video.writer import VideoWriter
