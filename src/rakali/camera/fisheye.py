""" Fisheye camera support """

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Tuple

import cv2 as cv
import numpy as np

from rakali.video.fps import cost

from .save import NumpyEncoder

logger = logging.getLogger(__name__)

STOP_CRITERIA = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.1)
CALIBRATE_FLAGS = cv.fisheye.CALIB_RECOMPUTE_EXTRINSIC + cv.fisheye.CALIB_CHECK_COND + cv.fisheye.CALIB_FIX_SKEW


def calibrate(object_points, image_points, image_size):
    """ Calibrate the camera using image points """

    obj_length = len(object_points)
    print(f'Calibrating on {obj_length} objects...')

    # zero holders
    K = np.zeros((3, 3))
    D = np.zeros((4, 1))
    rvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(obj_length)]
    tvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(obj_length)]

    ret, Kn, Dn, rvecsn, tvecsn = cv.fisheye.calibrate(
        objectPoints=object_points,
        imagePoints=image_points,
        image_size=image_size,
        K=K,
        D=D,
        rvecs=rvecs,
        tvecs=tvecs,
        flags=CALIBRATE_FLAGS,
        criteria=STOP_CRITERIA,
    )

    return ret, Kn, Dn, rvecsn, tvecsn


def save_calibration(
    calibration_file: str,
    K,
    D,
    rvecs,
    tvecs,
    image_size: Tuple[int, int],
    salt: int,
    pick_size: int,
    error: float,
    cid: str,
):
    """Save fisheye calibration to file"""

    logger.info(f'Saving fisheye calibration data to {calibration_file}')

    data = dict(
        K=K,
        D=D,
        rvecs=rvecs,
        tvecs=tvecs,
        image_size=image_size,
        salt=salt,
        pick_size=pick_size,
        error=error,
        cid=cid,
        time=time.time(),
    )
    dumped = json.dumps(data, cls=NumpyEncoder, indent=4, sort_keys=True)
    with open(calibration_file, 'w') as f:
        f.write(dumped)


def load_calibration(calibration_file):
    """Load fisheye calibration data from file"""

    logger.info(f'Loading fisheye calibration data from {calibration_file}')
    try:
        with open(calibration_file, 'r') as f:
            cal = json.load(f)
            return dict(
                K=np.asarray(cal['K']),
                D=np.asarray(cal['D']),
                rvecs=np.asarray(cal['rvecs']),
                tvecs=np.asarray(cal['tvecs']),
                image_size=tuple(cal['image_size']),
                salt=cal['salt'],
                pick_size=cal['pick_size'],
                error=cal['error'],
                cid=cal['cid'],
                time=cal['time'],
            )
    except IOError:
        print(f'{calibration_file} not found')
        return None


def get_maps(
    img,
    image_size,
    K,
    D,
    R=None,
    balance: float = 0.5,
    dim2=None,
    dim3=None,
    fov_scale=1,
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

    if R is None:
        R = np.eye(3)

    # use scaled_K, dim2 and balance to determine the final K used to un-distort image
    new_K = cv.fisheye.estimateNewCameraMatrixForUndistortRectify(
        K=scaled_K,
        D=D,
        image_size=dim2,
        R=R,
        balance=balance,
        fov_scale=fov_scale,
    )
    map1, map2 = cv.fisheye.initUndistortRectifyMap(
        K=scaled_K,
        D=D,
        R=R,
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
            self.calibration = None

    def set_calibration(self, calibration):
        """set calibration"""
        # TODO validate
        self.calibration = calibration

    @property
    def cid(self):
        """calibration id"""
        if self.calibration:
            return self.calibration.get('cid', 'UNSET')
        else:
            return 'UNSET'

    @property
    def calibration_time(self):
        """calibration time"""
        if self.calibration:
            return self.calibration.get('time', -1)
        else:
            return -1

    @property
    def calibration_time_formatted(self):
        """ formated calibration time """
        return datetime.fromtimestamp(self.calibration_time)

    def set_balance(self, balance, frame):
        self.balance = balance
        self.set_map(frame)

    def set_size(self, w, h, frame):
        if self.calibration:
            self.map1, self.map2 = get_maps(
                img=frame,
                image_size=(w, h),
                K=self.calibration['K'],
                D=self.calibration['D'],
                balance=self.balance,
                dim2=self.dim2,
                dim3=self.dim3,
            )
        else:
            logger.error('Load calibration before setting size')

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
