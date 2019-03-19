"""
Calibrate fisheye camera given set of chessboard images
"""

import click
import sys
import random
import numpy as np
import cv2 as cv
from pathlib import Path
import glob
import logging
from rakali.camera.chessboard import ChessboardFinder

from typing import Tuple

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_zero_object(pattern_size=(9, 6), square_size=0.023):
    columns, rows = pattern_size
    objp = np.zeros((1, rows * columns, 3), np.float32)
    objp[0, :, :2] = np.mgrid[0:rows, 0:columns].T.reshape(-1, 2)
    return objp


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


def load_image_points_file(save_file) -> Tuple[list, list, tuple]:
    """load from previously computed file """

    try:
        cache = np.load(save_file)
        logger.debug(f'Loading previously computed image points from {save_file}')
        return (
            list(cache['object_points']),
            list(cache['image_points']),
            tuple(cache['image_size']),
        )
    except IOError:
        logger.warning(f'{save_file} not found')
        return None


def get_points_from_chessboard_images(boards_path, chessboard_size, square_size):
    """
    Process folder with chesboard images and gather image points
    """
    logging.debug('Processing chessboard images...')

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
            logger.info(f'Ignoring {fname}')

    h, w = image_size
    return object_points, image_points, (w, h)


def calibrate(object_points, image_points, image_size):
    """
    Calibrate the pinhole camera using image points
    """
    N_OK = len(object_points)
    logging.debug(f'Calibrating on {N_OK} objects...')

    calibration_flags = cv.fisheye.CALIB_RECOMPUTE_EXTRINSIC + cv.fisheye.CALIB_CHECK_COND + cv.fisheye.CALIB_FIX_SKEW
    # zero holders
    K = np.zeros((3, 3))
    D = np.zeros((4, 1))
    rvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
    tvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]

    rms, _, _, _, _ = cv.fisheye.calibrate(
        objectPoints=object_points,
        imagePoints=image_points,
        image_size=image_size,
        K=K,
        D=D,
        rvecs=rvecs,
        tvecs=tvecs,
        flags=calibration_flags,
        criteria=(cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 1e-6),
    )

    return rms, K, D


def do_calibrate(
    input_folder,
    chessboard_size,
    square_size,
    calibration_file,
    image_points_file,
    salt=888,
    pick_size=50,
):
    # use previously computed image points if they are available
    exiting_points = load_image_points_file(image_points_file)
    if exiting_points:
        object_points, image_points, image_size = exiting_points
    else:
        object_points, image_points, image_size = get_points_from_chessboard_images(
            boards_path=input_folder,
            chessboard_size=chessboard_size,
            square_size=square_size,
        )
        save_image_points_file(
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

    rms, K, D = calibrate(
        object_points=object_points,
        image_points=image_points,
        image_size=image_size,
    )

    np.savez_compressed(
        calibration_file,
        K=K,
        D=D,
        image_size=image_size,
        seed=salt,
        k=pick_size,
    )

    print(f'DIM={image_size}')
    print(f'K=np.array({str(K.tolist())})')
    print(f'D=np.array({str(D.tolist())})')

    return rms


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
    default='fisheye_image_points.npz',
    show_default=True,
)
@click.option(
    '--calibration-file',
    help='Camera calibration data',
    default='fisheye_calibration.npz',
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

    error = do_calibrate(
        input_folder=input_folder,
        chessboard_size=(chessboard_columns, chessboard_rows),
        square_size=square_size,
        calibration_file=calibration_file,
        image_points_file=image_points_file,
        salt=salt,
        pick_size=pick_size,
    )
    click.secho(message=f'Calibration error: {error}')
