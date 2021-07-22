import logging
from typing import Tuple

import cv2 as cv
import numpy as np
from rakali.video import VideoStream

SIZE = (1920, 1080)

logger = logging.getLogger(__name__)


class VideoWriter:
    def __init__(
        self,
        size=SIZE,
        file_name="out.avi",
        fps=15,
        color=True,
        codec="MJPG",
    ):
        self.size = size
        self.file_name = file_name
        self.fps = fps
        self.color = color
        self.codec = codec

        self.writer = cv.VideoWriter(
            filename=file_name,
            fourcc=cv.VideoWriter_fourcc(*codec),
            fps=fps,
            frameSize=self.size,
            isColor=color,
        )

    def set_size(self, size):
        """set video frame size"""
        if size != self.size:
            self.writer.release()
            logger.debug(f"Reset frame size to {size}")
            self.writer = cv.VideoWriter(
                filename=self.file_name,
                fourcc=cv.VideoWriter_fourcc(*self.codec),
                fps=self.fps,
                frameSize=self.size,
                isColor=self.color,
            )
            self.size = size

    def write_noise(self):
        """write test noise frame"""
        self.writer.write(np.random.randint(0, 255, self.size).astype("uint8"))

    def write(self, frame):
        """write video frame to file"""
        if frame is not None:
            self.writer.write(frame)
        else:
            logger.warning("Frame is empty")

    def stereo_write(self, frames: Tuple):
        """write stereo video frames to file"""
        if len(frames) == 2:
            self.writer.write(np.hstack(frames))
        else:
            logger.warning("One of the frames were empty")

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.writer.release()


def get_stereo_writer(stream: VideoStream, file_name="out.avi"):
    """returns a stereo writer"""

    ok, frames = stream.read()
    if ok:
        video_size = frames.get_stereo_frame_size()
        logger.debug(f"Stereo video size {video_size}")
        return VideoWriter(size=video_size, file_name=file_name)
    else:
        logger.error("Could not get frame size")
