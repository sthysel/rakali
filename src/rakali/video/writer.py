import cv2 as cv
import numpy as np
import logging

SIZE = (480, 640, 3)

logger = logging.getLogger(__name__)


class VideoWriter:
    def __init__(
        self,
        size=SIZE,
        file_name='out.avi',
        fps=12,
        color=True,
    ):
        self.size = size
        print(size)
        self.writer = cv.VideoWriter(
            filename=file_name,
            fourcc=cv.VideoWriter_fourcc(*"MJPG"),
            fps=fps,
            frameSize=self.size[:2],
            isColor=color,
        )
        print(self.writer.getBackendName())

    def noise(self, frame_count=100):
        for frame in range(frame_count):
            self.writer.write(np.random.randint(0, 255, self.size).astype('uint8'))

        self.writer.release()

    def write(self, frame):
        if frame is not None:
            self.writer.write(frame)
        else:
            logger.warning('Frame is empty')

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.writer.getBackendName()
        self.writer.release()
