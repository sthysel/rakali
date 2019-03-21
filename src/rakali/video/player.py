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

    def __init__(
        self,
        stream: VideoStream = None,
        scale=1,
        window_name='Rakali Video',
        frame_callback=None,
    ):
        """Video player"""

        self.stream = stream
        self.scale = scale
        self.window_name = window_name
        self.callback = frame_callback

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

    def autoplay(self):
        """
        read the stream and display each frame, applying the callback to each
        frame
        """
        with self.stream as st:
            while cv.waitKey(1) & 0xFF != ord('q'):
                ok, frame = st.read()
                if ok:
                    img = self.rescale(frame)
                    if self.callback:
                        img = self.callback(img)
                    cv.imshow(self.window_name, img)
                else:
                    print('No more frames')
                    sys.exit()

        cv.destroyAllWindows()
        sys.exit()

    def show(self, frame):
        """ Show the frame """

        img = self.rescale(frame)
        if self.callback:
            img = self.callback(img)
        cv.imshow(self.window_name, img)
