"""
Assists with finding chessboards in a image stream
"""

from cv2 import cv


def get_chessboard_corners(frame, board_size=(6, 9)):
    """test if frame contains a checkerboard of appropiate size"""

    # Find the chess board corners
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    ret, corners = cv.findChessboardCorners(
        gray,
        board_size,
        cv.CALIB_CB_ADAPTIVE_THRESH + cv.CALIB_CB_NORMALIZE_IMAGE,
    )
    return ret, corners


def has_chessboard(frame, board_size=(6, 9)):
    ret, _ = get_chessboard_corners(frame=frame, board_size=board_size)
