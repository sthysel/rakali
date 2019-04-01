"""
Calibrate stereo fisheye camera rig given pairs of left/right chessboard images
"""

import click
import sys
import random
from pathlib import Path
import logging

from rakali.camera import fisheye
from rakali.camera import fisheye_stereo
from rakali.camera import chessboard

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@click.command(context_settings=dict(max_content_width=120))
@click.version_option()
@click.option(
    '-i',
    '--input-folder',
    help='Folder where chessboard images are stored',
    default='~/rakali/stereo/chessboards/',
    show_default=True,
)
@click.option(
    '--left-image-points-file',
    help='Left Corner points data',
    default='left_image_points.json',
    show_default=True,
)
@click.option(
    '--right-image-points-file',
    help='Right Corner points data',
    default='right_image_points.json',
    show_default=True,
)
@click.option(
    '--calibration-file',
    help='Stereo Camera calibration data',
    default='fisheye_stereo_calibration.json',
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
@click.option(
    '--cid',
    help='Calibration ID to associate a calibration file with a device',
    default='fisheye',
    show_default=True,
)
@click.option(
    '--prefilter/--no-prefilter',
    help='Prefilter images',
    default=False,
    show_default=True,
)
def cli(
    input_folder,
    left_image_points_file,
    right_image_points_file,
    calibration_file,
    chessboard_rows,
    chessboard_columns,
    square_size,
    salt,
    pick_size,
    cid,
    prefilter,
):
    """
    Calibrate fish-eye stereo camera rig using chessboard frames captured earlier.
    """

    if pick_size < 1:
        print(f'A set of {pick_size} is to small')
        sys.exit()

    # calibration chessboard images are loaded from this folder
    # there should be left/right image pairs
    input_folder = Path(input_folder).expanduser()
    if not input_folder.exists():
        click.secho(message=f'Folder {input_folder} does not exist', err=True)
        sys.exit()

    chessboard_size = (chessboard_columns, chessboard_rows)

    # filter through the calibration images and delete those that cannot be used
    # for calibration due to bad chessboard detection
    if prefilter:
        print('Pre-filtering calibration images to simplify the pipeline')
        chessboard.filter_unusable_pairs(
            boards_path=input_folder,
            chessboard_size=chessboard_size,
        )

    # calibrate each eye on it own, and then use the individual eye calibration
    # to perform a stereo calibration
    stereo_calibration = dict(chessboard_size=chessboard_size)
    for side, image_points_file in zip(('left', 'right'), (left_image_points_file, right_image_points_file)):
        # use previously computed image points if they are available
        exiting_points = chessboard.load_image_points_file(image_points_file)
        if exiting_points:
            object_points, image_points, image_size = exiting_points
        else:
            object_points, image_points, image_size = chessboard.get_points_from_chessboard_images(
                boards_path=input_folder,
                chessboard_size=chessboard_size,
                square_size=square_size,
                side=side,
            )
            chessboard.save_image_points_file(
                save_file=image_points_file,
                object_points=object_points,
                image_points=image_points,
                image_size=image_size,
                chessboard_size=chessboard_size,
            )

        # reduce points list else calibration takes too long
        random.seed(salt)
        image_points = random.choices(image_points, k=pick_size)
        object_points = object_points[:pick_size]

        rms, K, D, rvecs, tvecs = fisheye.calibrate(
            object_points=object_points,
            image_points=image_points,
            image_size=image_size,
        )
        stereo_calibration[side] = dict(
            rms=rms,
            K=K,
            D=D,
            rvecs=rvecs,
            tvecs=tvecs,
            image_points=image_points,
            object_points=object_points,
            image_size=image_size,
        )
        print(f'Calibrated {side} camera, error: {rms}')

    # perform stereo calibration using individual calibrations
    stereo_calibration_parameters = fisheye_stereo.stereo_calibrate(stereo_calibration)

    print(f'DIM={image_size}')
    for side in ('left', 'right'):
        cal = stereo_calibration[side]
        K = cal['K']
        D = cal['D']
        rms = cal['rms']

        print(f'{side} calibration')
        print(f'K=np.array({str(K.tolist())})')
        print(f'D=np.array({str(D.tolist())})')
        print(f'Calibration error: {rms}')

    fisheye_stereo.save_stereo_calibration(
        calibration_file,
        calibration_parameters=stereo_calibration_parameters,
        image_size=image_size,
        salt=salt,
        pick_size=pick_size,
        cid=cid,
    )
