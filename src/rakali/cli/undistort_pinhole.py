"""
Correct and display pinhole camera video stream
"""

import logging
from pathlib import Path

import click

from rakali import VideoPlayer
from rakali.camera import pinhole
from rakali.video import VideoFile, go
from rakali.annotate import add_frame_labels, colors

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


@click.command(context_settings=dict(max_content_width=120))
@click.version_option()
@click.option(
    '-s',
    '--source',
    help='Video source, can be local USB cam (0|1|2..) or IP cam rtsp URL or file',
    default="http://axis-lab/axis-cgi/mjpg/video.cgi?&camera=1",
    show_default=True,
)
@click.option(
    '--calibration-file',
    help='Camera calibration data',
    default='pinhole_calibration.npz',
    show_default=True,
)
def cli(source, calibration_file):
    """ Undistort live feed from pinhole model type camera """

    calibration_path = Path(calibration_file).expanduser()

    calibration = pinhole.load_calibration(calibration_file=calibration_path)
    stream = VideoFile(src=str(source))
    player = VideoPlayer()

    with stream, player:
        while go():
            ok, frame = stream.read()
            if ok:
                frame = pinhole.undistort(img=frame, calibration=calibration)
                frame = add_frame_labels(
                    frame=frame,
                    labels=[f'undistort cost: {pinhole.undistort.cost:6.3f}s'],
                    color=colors.get('WHITE'),
                )
                player.show(frame)
