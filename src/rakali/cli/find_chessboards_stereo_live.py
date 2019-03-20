"""
Find chessboards in both frames of a stereo feed
"""

import logging
import numpy as np

import cv2 as cv
import click
from pathlib import Path

from rakali.video import go
from rakali.stereo.reader import StereoCamera

from rakali.camera.chessboard import ChessboardFinder
from rakali import VideoPlayer
from rakali.annotate import add_frame_labels

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


@click.command(context_settings=dict(max_content_width=120))
@click.version_option()
@click.option(
    '-l',
    '--left-eye',
    help='Left eye, can be local USB cam (0|1|2..) or IP cam rtsp URL or file',
    default="http://axis-lab/axis-cgi/mjpg/video.cgi?&camera=1",
    show_default=True,
)
@click.option(
    '-r',
    '--right-eye',
    help='Right eye, can be local USB cam (0|1|2..) or IP cam rtsp URL or file',
    default="http://axis-lab/axis-cgi/mjpg/video.cgi?&camera=2",
    show_default=True,
)
@click.option(
    '-o',
    '--output-folder',
    help='Fetch image from URL',
    default='~/rakali/stereo/chessboards/',
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
def cli(left_eye, right_eye, output_folder, chessboard_rows, chessboard_columns):
    """
    Find chessboard calibration images in both frames of the stereo pair
    """

    out_path = Path(output_folder).expanduser()
    out_path.mkdir(parents=True, exist_ok=True)

    chessboard_size = (chessboard_columns, chessboard_rows)
    finder = ChessboardFinder(chessboard_size)

    stream = StereoCamera(
        left_src=left_eye,
        right_src=right_eye,
    )
    player = VideoPlayer()

    with player, stream:
        count = 0
        while go():
            ok, frames = stream.read()
            labels = [f'Stereo Calibrate']
            if ok:
                good = []
                annotated = []
                # so we have a good stereo frame, now inspect each frame and if
                # a chessboard is found in each, save the pair to disk.
                for frame in frames.frames():
                    display_frame = frame.copy()
                    has_corners, corners = finder.corners(frame)
                    if has_corners:
                        good.append(True)
                        finder.draw(display_frame, corners)
                        labels.append('CHESSBOARD')
                    else:
                        good.append(False)
                        labels.append('NO CHESSBOARD FOR YOU')
                    add_frame_labels(display_frame, labels=labels)
                    annotated.append(display_frame)
                if all(good):
                    for side, frame in frames.calibration_named_frames():
                        cv.imwrite(f'{out_path}/{side}_{count:05}.jpg', frame)
                    count += 1
                player.show(np.hstack(annotated))
