"""
Assists with finding chessboards in a image stream
"""

import glob
import os
import sys
import json
from typing import Tuple

import cv2 as cv
import numpy as np
from .save import NumpyEncoder

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


def load_image_points_file(save_file) -> Tuple[list, list, tuple]:
    """load from previously computed file """

    print(f'Loading previously computed image points from {save_file}')
    try:
        with open(save_file, 'r') as f:
            data = json.load(f)
            return (
                np.asarray(data['object_points']),
                np.asarray(data['image_points']),
                tuple(data['image_size']),
            )
    except IOError:
        print(f'{save_file} not found')
        return None


def save_image_points_file(
    save_file,
    object_points,
    image_points,
    image_size,
    chessboard_size,
):
    data = dict(
        object_points=object_points,
        image_points=image_points,
        image_size=image_size,
        chessboard_size=chessboard_size,
    )
    dumped = json.dumps(data, cls=NumpyEncoder, indent=4, sort_keys=True)
    with open(save_file, 'w') as f:
        f.write(dumped)


def get_zero_object(pattern_size=(9, 6), square_size=0.023):
    rows, columns = pattern_size  # no
    objp = np.zeros((1, rows * columns, 3), np.float32)
    objp[0, :, :2] = np.mgrid[0:rows, 0:columns].T.reshape(-1, 2)
    return objp


def get_points_from_chessboard_images(
    boards_path,
    chessboard_size,
    square_size,
    side='',
):
    """
    Process folder with chesboard images and gather image points
    """
    print('Processing chessboard images...')

    def check_size(image, image_size):
        if image_size is None:
            return img.shape[:2]
        else:
            if img.shape[:2] != image_size:
                print(f'Image {fname} size incorrect')
                sys.exit()
        return image_size

    image_size = None
    images = sorted(glob.glob(str(boards_path / f'{side}*.jpg')))
    zero = get_zero_object(
        square_size=square_size,
        pattern_size=chessboard_size,
    )
    finder = ChessboardFinder(chessboard_size)
    image_points = []
    object_points = []
    for fname in images:
        print(f'Processing chessboards file {fname}')
        img = cv.imread(fname)
        image_size = check_size(image=img, image_size=image_size)
        ok, corners = finder.corners(img, fast=False)
        if ok:
            image_points.append(corners)
            object_points.append(zero)
        else:
            print(f'No good chessboard corners in {fname}, ignoring')

    h, w = image_size
    return object_points, image_points, (w, h)


def filter_unusable_pairs(
    boards_path,
    chessboard_size,
):
    """ Run through image set and remove all pairs that fail the quality test"""

    def remove_pair(filename):
        """remove complementary pair if one of the pair is unfit """
        print(f'Removing complementary pair of which {filename} is part')
        _, rest = filename.split('_')
        pair = glob.glob(str(boards_path / f'*_{rest}'))
        for _file in pair:
            try:
                os.remove(_file)
            except OSError:
                print(f'Error deleting {_file}')
        return pair

    def check_size(image, image_size):
        if image_size is None:
            return img.shape[:2]
        else:
            if img.shape[:2] != image_size:
                print(f'Image {fname} size incorrect')
                remove_pair(fname)
        return image_size

    image_size = None
    images = glob.glob(str(boards_path / f'*.jpg'))
    finder = ChessboardFinder(chessboard_size)
    filtered = []
    for fname in images:
        # do not try and check a file that has been removed because its pair
        # was broken
        if fname in filtered:
            continue

        img = cv.imread(fname)
        image_size = check_size(image=img, image_size=image_size)
        ok, _ = finder.corners(img, fast=False)
        if ok:
            print(f'Image {fname} OK')
        else:
            filtered.extend(remove_pair(fname))
