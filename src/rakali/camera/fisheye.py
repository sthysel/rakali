"""
Fisheye camera support
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Tuple

import cv2 as cv
import numpy as np

from rakali.video.fps import cost

logger = logging.getLogger(__name__)

CAL_FLAGS = cv.fisheye.CALIB_RECOMPUTE_EXTRINSIC + cv.fisheye.CALIB_CHECK_COND + cv.fisheye.CALIB_FIX_SKEW


def stereo_calibrate(calibration_data):
    """ do stereo calibration on pre-calibrated cameras"""

    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.1)
    calib_flags = cv.fisheye.CALIB_RECOMPUTE_EXTRINSIC + cv.fisheye.CALIB_CHECK_COND + cv.fisheye.CALIB_FIX_SKEW

    # use left as std FIXME
    image_size = calibration_data['left']['image_size']
    object_points = calibration_data['left']['object_points']

    left_K = calibration_data['left']['K']
    left_D = calibration_data['left']['D']
    left_image_points = calibration_data['left']['image_points']

    right_K = calibration_data['right']['K']
    right_D = calibration_data['right']['D']
    right_image_points = calibration_data['right']['image_points']

    R = np.zeros((1, 1, 3), dtype=np.float64)
    T = np.zeros((1, 1, 3), dtype=np.float64)

    # bmf
    N_OK = len(left_image_points)
    object_points = np.reshape(object_points, (N_OK, 1, 6 * 9, 3))
    left_image_points = np.reshape(left_image_points, (N_OK, 1, 6 * 9, 2))
    right_image_points = np.reshape(right_image_points, (N_OK, 1, 6 * 9, 2))

    rms, K_left, D_left, K_right, D_right, R, T = cv.fisheye.stereoCalibrate(
        objectPoints=object_points,
        imagePoints1=left_image_points,
        imagePoints2=right_image_points,
        K1=left_K,
        D1=left_D,
        K2=right_K,
        D2=right_D,
        imageSize=image_size,
        R=R,
        T=T,
        # flags=calib_flags,
        # criteria=criteria,
    )
    print(rms)


def save_stereo_calibration(
    calibration_file,
    calibration_data,
    image_size,
    salt,
    pick_size,
    cid,
):
    """" Save calibration data """
    logger.info(f'Saving fisheye calibration data to {calibration_file}')

    left_object_points = calibration_data['left']['object_points']
    right_object_points = calibration_data['right']['object_points']

    assert (len(left_object_points) == len(right_object_points))

    left_K = calibration_data['left']['K'],
    left_D = calibration_data['left']['D'],
    left_rms = calibration_data['left']['rms'],
    left_image_points = calibration_data['left']['image_points'],

    right_K = calibration_data['right']['K'],
    right_D = calibration_data['right']['D'],
    right_rms = calibration_data['right']['rms'],
    right_image_points = calibration_data['right']['image_points'],

    np.savez_compressed(
        file=calibration_file,
        object_points=left_object_points,  # pick left both should be the same
        left_K=left_K,
        left_D=left_D,
        left_rms=left_rms,
        left_image_points=left_image_points,
        right_K=right_K,
        right_D=right_D,
        right_rms=right_rms,
        right_image_points=right_image_points,
        image_size=image_size,
        salt=salt,
        pick_size=pick_size,
        cid=cid,
        time=time.time(),
    )


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
    cid: str,
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
        cid=cid,
        time=time.time(),
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
        cid=str(cal['cid']),
        time=float(cal['time']),
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
