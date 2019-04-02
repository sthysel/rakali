"""
Stereo Fisheye camera support
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import numpy as np

import cv2 as cv
from rakali.video.fps import cost

from .fisheye import STOP_CRITERIA, get_maps, undistort
from .save import NumpyEncoder

logger = logging.getLogger(__name__)

CALIBRATE_FLAGS = cv.fisheye.CALIB_RECOMPUTE_EXTRINSIC + cv.fisheye.CALIB_CHECK_COND + cv.fisheye.CALIB_FIX_SKEW


def stereo_calibrate(calibration_data, use_pre_calibrated=True):
    """ do stereo calibration using pre-calibration values from left and right eyes """

    print('Calibrate Fisheye Stereo camera using pre-calibrated values')

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
    imgpoints_right = calibration_data['right']['image_points']

    # print(len(imgpoints_left), len(imgpoints_right))
    # with np.printoptions(precision=3, suppress=True):
    #     print(imgpoints_left)
    #     print(imgpoints_right)

    N_OK = len(imgpoints_left)

    objp = np.zeros((board_area, 1, 3), np.float64)
    objp[:, 0, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)

    objpoints = np.array([objp] * len(imgpoints_left), dtype=np.float64)
    imgpoints_left = np.asarray(imgpoints_left, dtype=np.float64)
    imgpoints_right = np.asarray(imgpoints_right, dtype=np.float64)

    objpoints = np.reshape(objpoints, (N_OK, 1, board_area, 3))
    imgpoints_left = np.reshape(imgpoints_left, (N_OK, 1, board_area, 2))
    imgpoints_right = np.reshape(imgpoints_right, (N_OK, 1, board_area, 2))

    # objpoints shape: (<num of calibration images>, 1, <num points in set>, 3)
    # imgpoints_left shape: (<num of calibration images>, 1, <num points in set>, 2)
    # imgpoints_right shape: (<num of calibration images>, 1, <num points in set>, 2)
    # print(objpoints.shape)
    # print(imgpoints_left.shape)
    # print(imgpoints_right.shape)

    rms, new_K_left, new_D_left, new_K_right, new_D_right, new_R, new_T = cv.fisheye.stereoCalibrate(
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
        flags=CALIBRATE_FLAGS,
        criteria=STOP_CRITERIA,
    )

    # return the combined calibration as well as the separately calibrated
    # metrics
    calibration = dict(
        rms=rms,
        individual_calibration=calibration_data,
        K_left=new_K_left,
        D_left=new_D_left,
        K_right=new_K_right,
        D_right=new_D_right,
        R=new_R,
        T=new_T,
    )
    print_calibration(calibration)
    return calibration


def save_stereo_calibration(
    calibration_file,
    calibration_parameters: dict,
    image_size,
    salt: int,
    pick_size: int,
    cid: str,
):
    """" Save calibration data """

    calibration_parameters['image_size'] = image_size
    calibration_parameters['salt'] = salt
    calibration_parameters['pick_size'] = pick_size
    calibration_parameters['cid'] = cid

    dumped = json.dumps(calibration_parameters, cls=NumpyEncoder, indent=4, sort_keys=True)
    with open(calibration_file, 'w') as f:
        f.write(dumped)


def load_stereo_calibration(calibration_file) -> dict:
    """load from previously computed file """

    print(f'Loading previously computed stereo calibration from {calibration_file}')
    try:
        with open(calibration_file, 'r') as f:
            data = json.load(f)
            # TODO ignore individual calibrations for now
            return dict(
                K_left=np.asarray(data['K_left']),
                K_right=np.asarray(data['K_right']),
                D_left=np.asarray(data['D_left']),
                D_right=np.asarray(data['D_right']),
                R=np.asarray(data['R']),
                T=np.asarray(data['T']),
                image_size=tuple(data['image_size']),
            )
    except IOError:
        print(f'{calibration_file} not found')
        return None


def print_calibration(calibration):
    """ Pretty print stereo fisheye calibration parameters """

    with np.printoptions(precision=3, suppress=True):
        print('K Left')
        print(calibration['K_left'])
        print('K Right')
        print(calibration['K_right'])
        print('D Left')
        print(calibration['D_left'])
        print('D Right')
        print(calibration['D_right'])

        print('R')
        print(calibration['R'])
        print('T')
        print(calibration['T'])


def calibration_labels(calibration, side):
    """calibration labels for annotating frames"""
    labels = []
    if side == 'left':
        with np.printoptions(precision=3, suppress=True):
            labels.extend('K\n{K_left}'.format(**calibration).split('\n'))
            labels.extend('D\n{D_left}'.format(**calibration).split('\n'))
            labels.extend('R\n{R}'.format(**calibration).split('\n'))
            labels.extend('T\n{T}'.format(**calibration).split('\n'))

    if side == 'right':
        with np.printoptions(precision=3, suppress=True):
            labels.extend('K\n{K_right}'.format(**calibration).split('\n'))
            labels.extend('D\n{D_right}'.format(**calibration).split('\n'))
            labels.extend('R\n{R}'.format(**calibration).split('\n'))
            labels.extend('T\n{T}'.format(**calibration).split('\n'))
    return labels


class CalibratedStereoFisheyeCamera:
    """ A Calibrated stereo fish-eye camera """

    def __init__(
        self,
        calibration_file,
        balance,
        dim2=None,
        dim3=None,
        name='stereo fisheye',
    ):
        self.balance = balance
        self.name = name
        self.dim2 = dim2
        self.dim3 = dim3
        if Path(calibration_file).exists():
            self.calibration = load_stereo_calibration(calibration_file=calibration_file)
        else:
            logger.error(f'Calibration file {calibration_file} does not exist')
            self.calibration = None

        print_calibration(self.calibration)
        self.set_stereo_rectify_parameters()

    def set_calibration(self, calibration):
        """set calibration"""
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

    def set_stereo_rectify_parameters(self):
        """ set rotation matrices """

        self.R_left, self.R_right, self.P1, self.P2, self.Q = cv.fisheye.stereoRectify(
            K1=self.calibration['K_left'],
            D1=self.calibration['D_left'],
            K2=self.calibration['K_right'],
            D2=self.calibration['D_right'],
            imageSize=self.calibration['image_size'],
            R=self.calibration['R'],
            tvec=self.calibration['T'],
            flags=cv.CALIB_ZERO_DISPARITY,
            balance=self.balance,
            fov_scale=1,
        )

    def set_maps(self, first_frame):
        """set the left and right maps"""

        if self.calibration:
            self.left_map1, self.left_map2 = get_maps(
                img=first_frame,
                image_size=self.calibration['image_size'],
                K=self.calibration['K_left'],
                D=self.calibration['D_left'],
                R=self.R_left,
                balance=self.balance,
                # dim2=self.dim2,
                # dim3=self.dim3,
            )
            self.right_map1, self.right_map2 = get_maps(
                img=first_frame,
                image_size=self.calibration['image_size'],
                K=self.calibration['K_right'],
                D=self.calibration['D_right'],
                R=self.R_right,
                balance=self.balance,
                # dim2=self.dim2,
                # dim3=self.dim3,
            )
        else:
            logger.error('Load calibration before setting the maps')

    @cost
    def correct(self, left, right):
        """undistort frames"""

        left_corrected = undistort(left, self.left_map1, self.left_map2)
        right_corrected = undistort(right, self.right_map1, self.right_map2)

        return (left_corrected, right_corrected)
