"""
Fisheye camera support
"""

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

CAL_FLAGS = cv.fisheye.CALIB_RECOMPUTE_EXTRINSIC + cv.fisheye.CALIB_CHECK_COND + cv.fisheye.CALIB_FIX_SKEW


def stereo_calibrate(calibration_data, use_pre_calibrated=True):
    """
    do stereo calibration using pre-calibration values from left and right eyes
    """

    print('Calibrate Fisheye Stereo camera using pre-calibrated values')

    calib_flags = cv.fisheye.CALIB_RECOMPUTE_EXTRINSIC + cv.fisheye.CALIB_CHECK_COND + cv.fisheye.CALIB_FIX_SKEW
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.1)

    chessboard_size = calibration_data['chessboard_size']
    board_area = chessboard_size[0] * chessboard_size[1]
    img_size = calibration_data['left']['image_size']

    if use_pre_calibrated:
        K_left = calibration_data['left']['K']
        D_left = calibration_data['left']['D']
        K_right = calibration_data['right']['K']
        D_right = calibration_data['right']['D']
    else:
        K_left = np.zeros((3, 3))
        D_left = np.zeros((4, 1))
        K_right = np.zeros((3, 3))
        D_right = np.zeros((4, 1))

    R = np.zeros((1, 1, 3), dtype=np.float64)
    T = np.zeros((1, 1, 3), dtype=np.float64)

    imgpoints_left = calibration_data['left']['image_points']
    imgpoints_right = calibration_data['left']['image_points']

    N_OK = len(imgpoints_left)

    objp = np.zeros((board_area, 1, 3), np.float64)
    objp[:, 0, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)

    objpoints = np.array([objp] * len(imgpoints_left), dtype=np.float64)
    imgpoints_left = np.asarray(imgpoints_left, dtype=np.float64)
    imgpoints_right = np.asarray(imgpoints_right, dtype=np.float64)

    objpoints = np.reshape(objpoints, (N_OK, 1, board_area, 3))
    imgpoints_left = np.reshape(imgpoints_left, (N_OK, 1, board_area, 2))
    imgpoints_right = np.reshape(imgpoints_right, (N_OK, 1, board_area, 2))

    rms, K_left, D_left, K_right, D_right, R, T = cv.fisheye.stereoCalibrate(
        objectPoints=objpoints,
        imagePoints1=imgpoints_left,
        imagePoints2=imgpoints_right,
        K1=K_left,
        D1=D_left,
        K2=K_right,
        D2=D_right,
        imageSize=img_size,
        R=R,
        T=T,
        flags=calib_flags,
        criteria=criteria,
    )

    # return the combined calibration as well as the separately calibrated
    # metrics
    return dict(
        rms=rms,
        individual_calibration=calibration_data,
        K_left=K_left,
        D_left=D_left,
        K_right=K_right,
        D_right=D_right,
        R=R,
        T=T,
    )


def save_stereo_calibration_nz(
    calibration_file,
    calibration_parameters: dict,
    image_size,
    salt: int,
    pick_size: int,
    cid: str,
):
    """" Save calibration data """
    logger.info(f'Saving fisheye calibration data to {calibration_file}')

    left_object_points = calibration_parameters['left']['object_points']
    right_object_points = calibration_parameters['right']['object_points']

    assert (len(left_object_points) == len(right_object_points))

    left_K = calibration_parameters['left']['K'],
    left_D = calibration_parameters['left']['D'],
    left_rms = calibration_parameters['left']['rms'],
    left_image_points = calibration_parameters['left']['image_points'],

    right_K = calibration_parameters['right']['K'],
    right_D = calibration_parameters['right']['D'],
    right_rms = calibration_parameters['right']['rms'],
    right_image_points = calibration_parameters['right']['image_points'],

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


def save_stereo_calibration(
    calibration_file,
    calibration_parameters: dict,
    image_size,
    salt: int,
    pick_size: int,
    cid: str,
):
    """" Save calibration data """

    dumped = json.dumps(calibration_parameters, cls=NumpyEncoder, indent=4, sort_keys=True)
    with open(calibration_file, 'w') as f:
        f.write(dumped)


def load_stereo_calibration(save_file) -> dict:
    """load from previously computed file """

    print(f'Loading previously computed stereo calibration from {save_file}')
    try:
        with open(save_file, 'r') as f:
            data = json.load(f)
            # TODO
            return (
                np.asarray(data['object_points']),
                np.asarray(data['image_points']),
                tuple(data['image_size']),
            )
    except IOError:
        print(f'{save_file} not found')
        return None


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
    """Save fisheye calibration to file"""

    logger.info(f'Saving fisheye calibration data to {calibration_file}')

    data = dict(
        K=K,
        D=D,
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
