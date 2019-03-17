#!/usr/bin/env python
"""
Calibrate pinhole camera given set of chessboard images
"""

import sys
import numpy as np
import cv2 as cv
from pathlib import Path
import glob
import logging
from rakali.camera.chessboard import ChessboardFinder

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_zero_object(size=(9, 6)):
    size = (9, 6)
    zero = np.zeros((size[0] * size[1], 3), np.float32)
    zero[:, :2] = np.mgrid[0:size[0], 0:size[1]].T.reshape(-1, 2)
    return zero


BOARDS = '~/calib/chessboards/pinhole/left/'
CALIBRATION = '~/calib/pinhole/left/calibration.npz'
calibration_save_file = Path(CALIBRATION).expanduser()

boards_path = Path(BOARDS).expanduser()
image_points_save_file = boards_path / 'image_points.npz'


def save_image_points_file(
    save_file,
    object_points,
    image_points,
    image_size,
):
    np.savez_compressed(
        save_file,
        object_points=object_points,
        image_points=image_points,
        image_size=image_size,
    )


def load_image_points_file(save_file=image_points_save_file):
    """load from previously computed file """

    try:
        cache = np.load(save_file)
        logger.debug(f'Loading previously computed image points from {save_file}')
        return (
            list(cache['object_points']),
            list(cache['image_points']),
            tuple(cache['image_size']),
        )
    except IOError:
        logger.warning(f"Cache file at {save_file} not found")
        return None


def get_points_from_chessboard_images(boards_path):
    """
    Process folder with chesboard images and gather image points
    """
    logging.debug('Processing chessboard images...')

    def check_size(image, image_size):
        if image_size is None:
            return img.shape[:2]
        else:
            if img.shape[:2] != image_size:
                print(f'Image {fname} size incorrect')
                sys.exit()
        return image_size

    image_size = None
    images = glob.glob(str(boards_path / '*.jpg'))
    zero = get_zero_object()
    finder = ChessboardFinder()
    image_points = []
    object_points = []
    for fname in images:
        img = cv.imread(fname)
        image_size = check_size(image=img, image_size=image_size)
        corners = finder.corners(img)
        if corners is not None:
            image_points.append(corners)
            object_points.append(zero)

    return object_points, image_points, image_size


def calibrate(object_points, image_points, image_size):
    """
    Calibrate the pinhole camera using image points
    """
    logging.debug('Calibrating...')
    _, camera_matrix, distortion_coefficients, _, _ = cv.calibrateCamera(
        objectPoints=object_points,
        imagePoints=image_points,
        imageSize=image_size,
        cameraMatrix=None,
        distCoeffs=None,
        # rvecs=None,
        # tvecs=None,
        # flags=None,
        # criteria=0,
    )
    return camera_matrix, distortion_coefficients


def save_calibration(
    calibration_file,
    camera_matrix,
    distortion_coefficients,
):
    np.savez_compressed(
        calibration_file,
        camera_matrix=camera_matrix,
        distortion_coefficients=distortion_coefficients,
    )


# use previously computed image points if they are available
exiting_points = load_image_points_file()
if exiting_points:
    object_points, image_points, image_size = exiting_points
    print(image_size)
    print(object_points[:1])
    print(image_points[:1])
else:
    object_points, image_points, image_size = get_points_from_chessboard_images(boards_path=boards_path)
    save_image_points_file(
        save_file=image_points_save_file,
        object_points=object_points,
        image_points=image_points,
        image_size=image_size,
    )

matrix, dist_coeff = calibrate(
    object_points=object_points,
    image_points=image_points,
    image_size=image_size,
)
save_calibration(
    calibration_file=calibration_save_file,
    camera_matrix=matrix,
    distortion_coefficients=dist_coeff,
)
print(matrix, dist_coeff)
