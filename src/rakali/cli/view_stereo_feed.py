""" View a stereo camera feed """

import logging
import numpy as np

import click

from rakali.video import VideoFile, go
from rakali.stereo.reader import StereoCamera

from rakali import VideoPlayer
from rakali.annotate import add_frame_labels, colors

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


def decorate_frame(frame, source):
    img = add_frame_labels(
        frame=frame,
        labels=[f'{source}'],
        color=colors.get('BHP'),
    )
    return img


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
def cli(left_eye, right_eye):
    # _decorate = partial(decorate_frame, source=source)
    stream = StereoCamera(
        left_src=left_eye,
        right_src=right_eye,
    )
    player = VideoPlayer()

    with player, stream:
        while go():
            ok, frames = stream.read()
            if ok:
                stack = np.hstack(frames.frames())
                player.show(stack)
