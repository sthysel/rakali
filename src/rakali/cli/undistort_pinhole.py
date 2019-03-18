#!/usr/bin/env python
"""
Correct and display pinhole camera video stream
"""

import logging
from pathlib import Path

import cv2 as cv
import numpy as np

from rakali import VideoPlayer, VideoStream, VideoWriter
from rakali.annotate import add_frame_labels, colors
from rakali.video import VideoFile, go
from rakali.video.fps import cost

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

SOURCE = '~/calib/pinhole/l.mkv'
source_path = Path(SOURCE).expanduser()

CALIBRATION = '~/calib/pinhole/left/calibration.npz'
calibration_save_file = Path(CALIBRATION).expanduser()


def load_calibration(calibration_file=calibration_save_file):
    logger.debug(f'Loading calibration data from {calibration_file}')
    cal = np.load(calibration_file)
    return dict(
        camera_matrix=cal['camera_matrix'],
        new_camera_matrix=cal['new_camera_matrix'],
        roi=cal['roi'],
        distortion_coefficients=cal['distortion_coefficients'],
        rotation=cal['rotation'],
        translation=cal['translation'],
        seed=int(cal['seed']),
        k=int(cal['k']),
        error=float(cal['error']),
    )


cal = load_calibration(calibration_file=calibration_save_file)


@cost
def undistort(img):
    img = cv.undistort(
        src=img,
        cameraMatrix=cal['camera_matrix'],
        distCoeffs=cal['distortion_coefficients'],
        dst=None,
        newCameraMatrix=cal['new_camera_matrix'],
    )
    img = add_frame_labels(
        frame=img,
        labels=[f'undistort cost: {undistort.cost:6.3f}ms'],
        color=colors.get('WHITE'),
    )
    return img


print(str(source_path))
stream = VideoFile(src=str(source_path))
player = VideoPlayer()

with stream, player:
    while go():
        ok, frame = stream.read()
        if ok:
            player.show(undistort(frame))
