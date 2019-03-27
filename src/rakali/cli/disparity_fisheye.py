"""
Show disparity map for rectified stereo fish eye images
"""

import sys
from pathlib import Path

import click
import cv2 as cv
import numpy as np

from rakali.annotate import add_frame_labels, colors
from rakali.camera.fisheye import CalibratedStereoFisheyeCamera


@click.command(context_settings=dict(max_content_width=120))
@click.version_option()
@click.argument(
    'image_number',
)
@click.option(
    '--chessboards-folder',
    help='Chessboard images store folder',
    default='~/rakali/stereo/chessboards/',
    show_default=True,
)
@click.option(
    '--calibration-file',
    help='Camera Camera calibration data',
    default='fisheye_stereo_calibration.json',
    type=click.Path(exists=True),
    show_default=True,
    required=True,
)
@click.option(
    '-b',
    '--balance',
    help='Balance value 0.0 ~30% pixel loss, 1.0 no loss',
    default=0.0,
    show_default=True,
)
@click.option(
    '-s',
    '--scale',
    help='Scale image',
    default=0.5,
    show_default=True,
)
def cli(image_number, chessboards_folder, calibration_file, balance, scale):
    """
    Load stereo fisheye images, correct them and display the disparity map
    """

    # get matching pair of images from folder
    left_frame, right_frame = get_frames(chessboards_folder, image_number)

    # get calibrated stereo rig
    camera = CalibratedStereoFisheyeCamera(
        calibration_file=calibration_file,
        balance=balance,
        dim2=None,
        dim3=None,  # remember we have these
    )

    # set correction maps
    camera.set_maps(left_frame)

    # unwarp pair images
    rectified = camera.correct(left_frame, right_frame)

    # display them
    original = np.hstack((left_frame, right_frame))
    corrected = np.hstack(rectified)
    quad = np.vstack((original, corrected))
    cv.imshow('Original and corrected', quad)

    while True:
        if cv.waitKey(1) & 0xFF == ord('q'):
            break


def get_frames(chessboards_folder, image_number):
    """get stereo frame pair """

    frames = []
    source = Path(chessboards_folder).expanduser()
    if not source.exists():
        print(f'Source folder {chessboards_folder} does not exist')
        sys.exit()

    for side in ('left', 'right'):
        fname = f'{side}_{image_number}.jpg'
        file_path = source / Path(fname)
        print(f'loading {file_path}')
        if not file_path.exists():
            print(f'{side} image file {file_path} does not exist')
            sys.exit()
        frames.append(cv.imread(str(file_path)))
    return frames


def label_frame(camera, frame):
    labels = [
        f'Reprojected fisheye frame',
        f'undistort cost: {camera.correct.cost:6.3f}s',
        f'balance: {camera.balance}',
        f'cid: {camera.cid} calibrated on {camera.calibration_time_formatted}',
        # f'dim2 {dim2}',
        # f'dim3 {dim3}',
    ]
    labeled_frame = add_frame_labels(
        frame=frame,
        labels=labels,
        color=colors.get('BHP'),
    )
    return labeled_frame
