#!/usr/bin/env python
"""
Calibrate pinhole camera given set of chessboard images
"""

import sys
import random
import numpy as np
import cv2 as cv
from pathlib import Path
import glob
import logging
from rakali.camera.chessboard import ChessboardFinder

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_zero_object(size=(9, 6)):
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

    h, w = image_size
    return object_points, image_points, (w, h)


def calibrate(object_points, image_points, image_size):
    """
    Calibrate the pinhole camera using image points
    """
    logging.debug('Calibrating...')
    _, camera_matrix, distortion_coefficients, rotation, translation = cv.calibrateCamera(
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
    return camera_matrix, distortion_coefficients, rotation, translation


def reprojection_error(object_points, image_points, rotation, translation, camera_matrix, distortion):
    total_error = 0
    length = len(object_points)
    for i in range(length):
        __imgpoints2, _ = cv.projectPoints(object_points[i], rotation[i], translation[i], camera_matrix, distortion)
        error = cv.norm(image_points[i], __imgpoints2, cv.NORM_L2) / len(__imgpoints2)
        total_error += error

    return total_error / length


def do_calibrate(calibration_file=calibration_save_file, seed=128, k=50):
    # use previously computed image points if they are available
    exiting_points = load_image_points_file()
    if exiting_points:
        object_points, image_points, image_size = exiting_points
    else:
        object_points, image_points, image_size = get_points_from_chessboard_images(boards_path=boards_path)
        save_image_points_file(
            save_file=image_points_save_file,
            object_points=object_points,
            image_points=image_points,
            image_size=image_size,
        )

    w, h = image_size
    assert(w > h)
    # reduce points list else calibration takes too long
    random.seed(seed)
    image_points = random.choices(image_points, k=k)
    object_points = object_points[:k]

    matrix, dist_coeff, rotation, translation = calibrate(
        object_points=object_points,
        image_points=image_points,
        image_size=image_size,
    )

    new_camera_matrix, roi = cv.getOptimalNewCameraMatrix(
        cameraMatrix=matrix,
        distCoeffs=dist_coeff,
        imageSize=image_size,
        alpha=1,
        newImgSize=image_size,
    )

    error = reprojection_error(object_points, image_points, rotation, translation, matrix, dist_coeff)
    np.savez_compressed(
        calibration_file,
        camera_matrix=matrix,
        new_camera_matrix=new_camera_matrix,
        roi=roi,
        distortion_coefficients=dist_coeff,
        rotation=rotation,
        translation=translation,
        seed=seed,
        k=k,
        error=error,
    )
    print(f'Reprojection error {error}')


do_calibrate()
