import cv2 as cv
import numpy as np

SIZE = (480, 640, 3)


class VideoWriter:
    def __init__(self, size=SIZE):
        self.size = size
        self.writer = cv.VideoWriter(
            "output.avi",
            cv.VideoWriter_fourcc(*"MJPG"),
            30,
            self.size[:2],
        )

    def noise(self, frame_count=100):
        for frame in range(frame_count):
            self.writer.write(
                np.random.randint(0, 255, self.size).astype('uint8'), )

        self.writer.release()

    def write(self, frame):
        self.writer.write(frame).astype('uint8')

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.writer.release()
