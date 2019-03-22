"""
Support for pinhole camera
"""

import sys
import numpy as np
import cv2 as cv
import glob
import logging
from rakali.camera.chessboard import ChessboardFinder

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_zero_object(pattern_size=(9, 6), square_size=0.023):
    pattern_points = np.zeros((np.prod(pattern_size), 3), np.float32)
    pattern_points[:, :2] = np.indices(pattern_size).T.reshape(-1, 2)
    pattern_points *= square_size
    return pattern_points


def load_image_points_file(save_file):
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


def get_points_from_chessboard_images(
    boards_path,
    chessboard_size,
    square_size,
):
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
    zero = get_zero_object(
        square_size=square_size,
        pattern_size=chessboard_size,
    )
    finder = ChessboardFinder(chessboard_size)
    image_points = []
    object_points = []
    for fname in images:
        img = cv.imread(fname)
        image_size = check_size(image=img, image_size=image_size)
        ok, corners = finder.corners(img, fast=False)
        if ok:
            image_points.append(corners)
            object_points.append(zero)
        else:
            logger.info(f'Ignoring {fname}')

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


def reprojection_error(
    object_points,
    image_points,
    rotation,
    translation,
    camera_matrix,
    distortion,
):
    """ Calculate reprojection error"""

    total_error = 0
    length = len(object_points)
    for i in range(length):
        __imgpoints, _ = cv.projectPoints(
            objectPoints=object_points[i],
            rvec=rotation[i],
            tvec=translation[i],
            cameraMatrix=camera_matrix,
            distCoeffs=distortion,
        )
        error = cv.norm(image_points[i], __imgpoints, cv.NORM_L2) / len(__imgpoints)
        total_error += error

    return total_error / length
