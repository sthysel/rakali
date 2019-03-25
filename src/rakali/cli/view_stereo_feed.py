""" View a stereo camera feed """

import logging
import numpy as np

import click

from rakali.video import go
from rakali.stereo.reader import StereoCamera

from rakali import VideoPlayer
from rakali.annotate import add_frame_labels, colors

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


def decorate_frame(frame, side, count, source):
    img = add_frame_labels(
        frame=frame,
        labels=[
            f'{side}',
            f'{source}',
            f'frame # {count}',
        ],
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
    stream = StereoCamera(
        left_src=left_eye,
        right_src=right_eye,
    )
    player = VideoPlayer()

    with player, stream:
        count = 0
        while go():
            ok, frames = stream.read()
            if ok:
                count += 1
                annotated = []
                for side, source, frame in zip(('left', 'right'), (left_eye, right_eye), frames.frames()):
                    annotated.append(decorate_frame(
                        frame=frame,
                        side=side,
                        count=count,
                        source=source,
                    ))
                stack = np.hstack(annotated)
                player.show(stack)
