"""
Calibrate pinhole camera given set of chessboard images
"""

import click
import sys
import random
import numpy as np
import cv2 as cv
from pathlib import Path
import logging
from rakali.camera import pinhole

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@click.command(context_settings=dict(max_content_width=120))
@click.version_option()
@click.option(
    '-i',
    '--input-folder',
    help='Folder where chessboard images are stored',
    default='~/rakali/chessboards/',
    show_default=True,
)
@click.option(
    '--image-points-file',
    help='Corner points data',
    default='image_points.npz',
    show_default=True,
)
@click.option(
    '--calibration-file',
    help='Camera calibration data',
    default='pinhole_calibration.npz',
    show_default=True,
)
@click.option(
    '--chessboard-rows',
    help='Chessboard rows',
    default=9,
    show_default=True,
)
@click.option(
    '--chessboard-columns',
    help='Chessboard columns',
    default=6,
    show_default=True,
)
@click.option(
    '--square-size',
    help='Chessboard square size in m',
    default=0.023,
    show_default=True,
)
@click.option(
    '--salt',
    help='Seed value for random picking of calibration images from a large set',
    default=888,
    show_default=True,
)
@click.option(
    '--pick-size',
    help='Size of image set to use for calibration, picked from available set',
    default=50,
    show_default=True,
)
def cli(
    input_folder,
    image_points_file,
    calibration_file,
    chessboard_rows,
    chessboard_columns,
    square_size,
    salt,
    pick_size,
):
    """
    Calibrate pinhole camera using chessboard frames captured earlier.
    """

    if pick_size < 5:
        print(f'A set of {pick_size} is to small')
        sys.exit()

    input_folder = Path(input_folder).expanduser()

    if not input_folder.exists():
        click.secho(message=f'Folder {input_folder} does not exist', err=True)
        sys.exit()

    chessboard_size = (chessboard_columns, chessboard_rows)

    # use previously computed image points if they are available
    exiting_points = pinhole.load_image_points_file(image_points_file)
    if exiting_points:
        object_points, image_points, image_size = exiting_points
    else:
        object_points, image_points, image_size = pinhole.get_points_from_chessboard_images(
            boards_path=input_folder,
            chessboard_size=chessboard_size,
            square_size=square_size,
        )
        pinhole.save_image_points_file(
            save_file=image_points_file,
            object_points=object_points,
            image_points=image_points,
            image_size=image_size,
        )

    w, h = image_size
    assert (w > h)

    # reduce points list else calibration takes too long
    random.seed(salt)
    image_points = random.choices(image_points, k=pick_size)
    object_points = object_points[:pick_size]

    matrix, dist_coeff, rotation, translation = pinhole.calibrate(
        object_points=object_points,
        image_points=image_points,
        image_size=image_size,
    )

    new_camera_matrix, roi = cv.getOptimalNewCameraMatrix(
        cameraMatrix=matrix,
        distCoeffs=dist_coeff,
        imageSize=image_size,
        alpha=1,
        newImgSize=image_size,
    )

    error = pinhole.reprojection_error(object_points, image_points, rotation, translation, matrix, dist_coeff)

    pinhole.save_calibration(
        calibration_file,
        camera_matrix=matrix,
        new_camera_matrix=new_camera_matrix,
        roi=roi,
        distortion_coefficients=dist_coeff,
        rotation=rotation,
        translation=translation,
        salt=salt,
        pick_size=pick_size,
        error=error,

    )

    click.secho(message=f'Calibration error: {error}')
