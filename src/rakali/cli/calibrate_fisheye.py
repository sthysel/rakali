"""
Calibrate fisheye camera given set of chessboard images
"""

import logging
import random
import sys
from pathlib import Path

import click

# from rakali.camera.fisheye import save_calibration
from rakali.camera import chessboard, fisheye

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@click.command(context_settings=dict(max_content_width=120))
@click.version_option()
@click.option(
    "-i",
    "--input-folder",
    help="Folder where chessboard images are stored",
    default="~/rakali/chessboards/",
    show_default=True,
)
@click.option(
    "--image-points-file",
    help="Corner points data",
    default="image_points.json",
    show_default=True,
)
@click.option(
    "--calibration-file",
    help="Camera calibration data",
    default="fisheye_calibration.json",
    show_default=True,
)
@click.option(
    "--chessboard-rows",
    help="Chessboard rows",
    default=9,
    show_default=True,
)
@click.option(
    "--chessboard-columns",
    help="Chessboard columns",
    default=6,
    show_default=True,
)
@click.option(
    "--square-size",
    help="Chessboard square size in m",
    default=0.023,
    show_default=True,
)
@click.option(
    "--salt",
    help="Seed value for random picking of calibration images from a large set",
    default=888,
    show_default=True,
)
@click.option(
    "--pick-size",
    help="Size of image set to use for calibration, picked from available set",
    default=50,
    show_default=True,
)
@click.option(
    "--cid",
    help="Calibration ID to associate a calibration file with a device",
    default="fisheye",
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
    cid,
):
    """
    Calibrate fish-eye camera using chessboard frames captured earlier.
    """

    if pick_size < 5:
        print(f"A set of {pick_size} is to small")
        sys.exit()

    input_folder = Path(input_folder).expanduser()
    if not input_folder.exists():
        click.secho(message=f"Folder {input_folder} does not exist", err=True)
        sys.exit()

    chessboard_size = (chessboard_columns, chessboard_rows)

    # use previously computed image points if they are available
    exiting_points = chessboard.load_image_points_file(image_points_file)
    if exiting_points:
        object_points, image_points, image_size = exiting_points
    else:
        (
            object_points,
            image_points,
            image_size,
        ) = chessboard.get_points_from_chessboard_images(
            boards_path=input_folder,
            chessboard_size=chessboard_size,
            square_size=square_size,
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

    rms, K, D = fisheye.calibrate(
        object_points=object_points,
        image_points=image_points,
        image_size=image_size,
    )

    fisheye.save_calibration(
        calibration_file,
        K=K,
        D=D,
        image_size=image_size,
        salt=salt,
        pick_size=pick_size,
        error=rms,
        cid=cid,
    )

    print(f"DIM={image_size}")
    print(f"K=np.array({str(K.tolist())})")
    print(f"D=np.array({str(D.tolist())})")
    click.secho(message=f"Calibration error: {rms}")
