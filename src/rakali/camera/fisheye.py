"""
Fisheye camera support
"""

import logging
import sys
from pathlib import Path
from typing import Tuple

import glob
import cv2 as cv
import numpy as np

from rakali.video.fps import cost

from .chessboard import ChessboardFinder

logger = logging.getLogger(__name__)

CAL_FLAGS = cv.fisheye.CALIB_RECOMPUTE_EXTRINSIC + cv.fisheye.CALIB_CHECK_COND + cv.fisheye.CALIB_FIX_SKEW


def get_zero_object(pattern_size=(9, 6), square_size=0.023):
    rows, columns = pattern_size  # no
    objp = np.zeros((1, rows * columns, 3), np.float32)
    objp[0, :, :2] = np.mgrid[0:rows, 0:columns].T.reshape(-1, 2)
    return objp


def load_image_points_file(save_file) -> Tuple[list, list, tuple]:
    """load from previously computed file """

    try:
        cache = np.load(save_file)
        print(f'Loading previously computed image points from {save_file}')
        return (
            list(cache['object_points']),
            list(cache['image_points']),
            tuple(cache['image_size']),
        )
    except IOError:
        print(f'{save_file} not found')
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
            print(f'Ignoring {fname}')

    h, w = image_size
    return object_points, image_points, (w, h)


def calibrate(object_points, image_points, image_size):
    """
    Calibrate the pinhole camera using image points
    """
    obj_length = len(object_points)
    print(f'Calibrating on {obj_length} objects...')

    # zero holders
    K = np.zeros((3, 3))
    D = np.zeros((4, 1))
    rvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(obj_length)]
    tvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(obj_length)]

    rms, _, _, _, _ = cv.fisheye.calibrate(
        objectPoints=object_points,
        imagePoints=image_points,
        image_size=image_size,
        K=K,
        D=D,
        rvecs=rvecs,
        tvecs=tvecs,
        flags=CAL_FLAGS,
        criteria=(cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 1e-6),
    )

    return rms, K, D


def save_calibration(
    calibration_file: str,
    K,
    D,
    image_size: Tuple[int, int],
    salt: int,
    pick_size: int,
    error: float,
):
    """Save fisheye calibation to file"""
    logger.info(f'Saving fisheye calibration data to {calibration_file}')
    np.savez_compressed(
        calibration_file,
        K=K,
        D=D,
        image_size=image_size,
        salt=salt,
        pick_size=pick_size,
        error=error,
    )


def load_calibration(calibration_file):
    """Load fisheye calibration data from file"""
    logger.info(f'Loading fisheye calibration data from {calibration_file}')
    cal = np.load(calibration_file)
    return dict(
        K=cal['K'],
        D=cal['D'],
        image_size=cal['image_size'],
        salt=int(cal['salt']),
        pick_size=int(cal['pick_size']),
        error=float(cal['error']),
    )


def get_maps(
    img,
    image_size,
    K,
    D,
    balance: float = 0.5,
    dim2=None,
    dim3=None,
):
    """calculate fish-eye reprojection maps"""

    dim1 = img.shape[:2][::-1]
    assert dim1[0] / dim1[1] == image_size[0] / image_size[
        1], "Image to undistort needs to have same aspect ratio as the ones used in calibration"

    if not dim2:
        dim2 = dim1
    if not dim3:
        dim3 = dim1
    # The values of K is to scale with image dimension.
    scaled_K = K * dim1[0] / image_size[0]
    scaled_K[2][2] = 1.0  # Except that K[2][2] is always 1.0

    # use scaled_K, dim2 and balance to determine the final K used to un-distort image
    new_K = cv.fisheye.estimateNewCameraMatrixForUndistortRectify(
        K=scaled_K,
        D=D,
        image_size=dim2,
        R=np.eye(3),
        balance=balance,
    )
    map1, map2 = cv.fisheye.initUndistortRectifyMap(
        K=scaled_K,
        D=D,
        R=np.eye(3),
        P=new_K,
        size=dim3,
        m1type=cv.CV_16SC2,
    )
    return map1, map2


@cost
def undistort(img, map1, map2):
    """undistort fisheye image"""

    undistorted_img = cv.remap(
        src=img,
        map1=map1,
        map2=map2,
        interpolation=cv.INTER_LINEAR,
        borderMode=cv.BORDER_CONSTANT,
    )

    return undistorted_img


class CalibratedFisheyeCamera:
    """ A Calibrated fish-eye camera """

    def __init__(
        self,
        calibration_file,
        balance,
        dim2=None,
        dim3=None,
        name='fisheye',
    ):
        self.balance = balance
        self.name = name
        self.dim2 = dim2
        self.dim3 = dim3
        if Path(calibration_file).exists():
            self.calibration = load_calibration(calibration_file=calibration_file)
        else:
            logger.error(f'Calibration file {calibration_file} does not exist')

    def set_map(self, first_frame):
        """set the maps"""
        if self.calibration:
            self.map1, self.map2 = get_maps(
                img=first_frame,
                image_size=self.calibration['image_size'],
                K=self.calibration['K'],
                D=self.calibration['D'],
                balance=self.balance,
                dim2=self.dim2,
                dim3=self.dim3,
            )
        else:
            logger.error('Load calibration before setting the map')

    @cost
    def correct(self, frame):
        """undistort frame"""
        return undistort(frame, self.map1, self.map2)
