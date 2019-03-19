"""
Correct and display pinhole camera video stream
"""

import logging
from pathlib import Path

import click
import cv2 as cv
import numpy as np

from rakali import VideoPlayer
from rakali.annotate import add_frame_labels, colors
from rakali.video import VideoFile, go
from rakali.video.fps import cost

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


def load_calibration(calibration_file):
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


@cost
def undistort(img, calibration):
    img = cv.undistort(
        src=img,
        cameraMatrix=calibration['camera_matrix'],
        distCoeffs=calibration['distortion_coefficients'],
        dst=None,
        newCameraMatrix=calibration['new_camera_matrix'],
    )
    img = add_frame_labels(
        frame=img,
        labels=[f'undistort cost: {undistort.cost:6.3f}ms'],
        color=colors.get('WHITE'),
    )
    return img


@click.command(context_settings=dict(max_content_width=120))
@click.version_option()
@click.option(
    '-s',
    '--source',
    help='Video source, can be local USB cam (0|1|2..) or IP cam rtsp URL or file',
    default="rtsp://10.41.212.144/axis-media/media.amp?camera=1",
    show_default=True,
)
@click.option(
    '--calibration-file',
    help='Camera calibration data',
    default='calibration.npz',
    show_default=True,
)
def cli(source, calibration_file):

    CALIBRATION = '~/calib/pinhole/left/calibration.npz'
    calibration_file = Path(CALIBRATION).expanduser()

    calibration = load_calibration(calibration_file=calibration_file)
    stream = VideoFile(src=str(source))
    player = VideoPlayer()

    with stream, player:
        while go():
            ok, frame = stream.read()
            if ok:
                player.show(undistort(img=frame, calibration=calibration))
