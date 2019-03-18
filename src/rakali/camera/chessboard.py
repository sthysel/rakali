"""
Assists with finding chessboards in a image stream
"""

import cv2 as cv

from ..video import cost

CALIB_FLAGS_THOROUGH = cv.CALIB_CB_ADAPTIVE_THRESH + cv.CALIB_CB_NORMALIZE_IMAGE + cv.CALIB_CB_FAST_CHECK
CALIB_FLAGS_FAST = cv.CALIB_CB_FAST_CHECK
SUBPIXEL_CRITERIA = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.1)


class ChessboardFinder:
    def __init__(
        self,
        chessboard_size=(6, 9),
    ):
        self.size = chessboard_size

    def get_chessboard_corners(self, gray, fast=True):
        """test if frame contains a checkerboard of appropiate size"""

        if fast:
            flags = CALIB_FLAGS_FAST
        else:
            flags = CALIB_FLAGS_THOROUGH

        ret, corners = cv.findChessboardCorners(
            image=gray,
            patternSize=self.size,
            flags=flags,
        )
        return ret, corners

    def refine_corners(self, gray, corners):
        cv.cornerSubPix(
            image=gray,
            corners=corners,
            winSize=(3, 3),
            zeroZone=(-1, -1),
            criteria=SUBPIXEL_CRITERIA,
        )
        return corners

    def corners(self, frame, fast=True):
        """ Get the corners for calibration"""
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        ret, corners = self.get_chessboard_corners(gray, fast=fast)
        if ret:
            return ret, self.refine_corners(gray=gray, corners=corners)
        else:
            return ret, None

    @cost
    def has_chessboard(self, frame):
        """boolean test for chessboard pressense in frame """
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        ret, _ = self.get_chessboard_corners(gray=gray)
        return ret

    def draw(self, frame, corners):
        """Draw the chessboard corners"""
        return cv.drawChessboardCorners(frame, self.size, corners, True)
