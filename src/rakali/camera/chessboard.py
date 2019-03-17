"""
Assists with finding chessboards in a image stream
"""

import cv2 as cv

from ..video import cost

CALIB_FLAGS = cv.CALIB_CB_ADAPTIVE_THRESH + cv.CALIB_CB_NORMALIZE_IMAGE + cv.CALIB_CB_FAST_CHECK
SUBPIXEL_CRITERIA = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.1)


class ChessboardFinder:
    def __init__(
        self,
        chessboard_size=(6, 9),
    ):
        self.size = chessboard_size

    def get_chessboard_corners(self, gray):
        """test if frame contains a checkerboard of appropiate size"""

        # Find the chess board corners
        ret, corners = cv.findChessboardCorners(
            image=gray,
            patternSize=self.size,
            flags=CALIB_FLAGS,
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

    def corners(self, frame):
        """ Get the corners for calibration"""
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        ret, corners = self.get_chessboard_corners(gray)
        if ret:
            return self.refine_corners(gray=gray, corners=corners)
        else:
            None

    @cost
    def has_chessboard(self, frame):
        """boolean test for chessboard pressense in frame """
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        ret, _ = self.get_chessboard_corners(gray=gray)
        return ret
