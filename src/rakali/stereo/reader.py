import logging
import sys
import time
from typing import Tuple

from rakali.video.reader import VideoStream

logger = logging.getLogger(__name__)


class StereoFrame:
    """ a set of time-synced frames """

    def __init__(
        self,
        left,
        right,
        left_name='left',
        right_name='right',
        timestamp=None,
    ):

        if timestamp is None:
            timestamp = time.time()
        self.timestamp = timestamp

        self.left_name = left_name
        self.right_name = right_name

        self.left = left
        self.right = right

    def frames(self):
        """return lef, right frames"""
        return (self.left, self.right)

    def calibration_named_frames(self):
        """
        the calibration process dumps files to disk and needs to find them
        later on. This function just names frames to the standard left, right
        convention allowing the user to annotate the frames to will and not
        break the calibration pipeline
        """

        return (('left', self.left), ('right', self.right))

    def is_good(self):
        return (self.left is not None) and (self.right is not None)

    def get_stereo_frame_size(self) -> Tuple[int, int]:
        """the size of a horizontally stacked stereo frame"""

        h, w = self.left.shape[:2]
        return (w * 2, h)


class StereoCamera:
    """
    A stereo pair of cameras.

    This class allows both cameras in a stereo pair to be read
    simultaneously.
    """

    def __init__(self, left_src: str, right_src: str):
        """
        Initialize cameras.

        left_url and right_url are the Axis IP cammera urls
        """

        if left_src.strip() != right_src.strip():
            self.right_reader = VideoStream(name='Left', src=left_src)
            self.left_reader = VideoStream(name='Right', src=right_src)
        else:
            logger.error('Stream sources are identical')
            sys.exit()

    def __enter__(self):
        for reader in (self.left_reader, self.right_reader):
            reader.start()
        return self

    def __exit__(self, type, value, traceback):
        for reader in (self.left_reader, self.right_reader):
            reader.stop()

    def read(self) -> Tuple[bool, StereoFrame]:
        """Get current frames from cameras."""

        _, left = self.left_reader.read()
        _, right = self.right_reader.read()
        frame = StereoFrame(
            left=left,
            right=right,
        )

        return frame.is_good(), frame
