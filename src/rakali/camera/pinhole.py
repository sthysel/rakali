"""
Support for pinhole camera
"""

import logging
import time
from pathlib import Path

import cv2 as cv
import numpy as np

from rakali.video.fps import cost

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def xxx_get_zero_object(pattern_size=(9, 6), square_size=0.023):
    pattern_points = np.zeros((np.prod(pattern_size), 3), np.float32)
    pattern_points[:, :2] = np.indices(pattern_size).T.reshape(-1, 2)
    pattern_points *= square_size
    return pattern_points


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


def save_calibration(
    calibration_file: str,
    camera_matrix,
    new_camera_matrix,
    roi,
    distortion_coefficients,
    rotation,
    translation,
    salt: int,
    pick_size: int,
    error: float,
    cid: str,
):
    """Save pinhole calibration to file """
    np.savez_compressed(
        calibration_file,
        camera_matrix=camera_matrix,
        new_camera_matrix=new_camera_matrix,
        roi=roi,
        distortion_coefficients=distortion_coefficients,
        rotation=rotation,
        translation=translation,
        salt=salt,
        pick_size=pick_size,
        error=error,
        cid=cid,
        time=time.time(),
    )


def load_calibration(calibration_file):
    """Load pinhole calibration"""
    logger.debug(f'Loading calibration data from {calibration_file}')
    cal = np.load(calibration_file)
    return dict(
        camera_matrix=cal['camera_matrix'],
        new_camera_matrix=cal['new_camera_matrix'],
        roi=cal['roi'],
        distortion_coefficients=cal['distortion_coefficients'],
        rotation=cal['rotation'],
        translation=cal['translation'],
        salt=int(cal['salt']),
        pick_size=int(cal['pick_size']),
        error=float(cal['error']),
        cid=str(cal['cid']),
        time=float(cal['time']),
    )


@cost
def undistort(img, calibration):
    img = cv.undistort(
        src=img,
        cameraMatrix=calibration['camera_matrix'],
        distCoeffs=calibration['distortion_coefficients'],
        dst=None,
        newCameraMatrix=calibration['new_camera_matrix'],
    )
    return img


class CalibratedPinholeCamera:
    """ A calibrated pinhole camera """

    def __init__(
        self,
        calibration_file,
        name='pinhole',
    ):
        self.name = name
        if Path(calibration_file).exists():
            self.calibration = load_calibration(calibration_file=calibration_file)
        else:
            logger.error(f'Calibration file {calibration_file} does not exist')

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

    @cost
    def correct(self, frame):
        """undistort frame"""
        return undistort(frame, self.calibration)
