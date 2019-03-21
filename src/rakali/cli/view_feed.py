"""
View feed directly from camera
"""

import logging

from functools import partial
import click

from rakali import VideoPlayer
from rakali.video import VideoStream
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
    '-s',
    '--source',
    help='Video source, can be local USB cam (0|1|2..) or IP cam rtsp URL or file',
    default="http://axis-lab/axis-cgi/mjpg/video.cgi?&camera=2",
    show_default=True,
)
def cli(source):
    _decorate = partial(decorate_frame, source=source)
    stream = VideoStream(src=source)
    player = VideoPlayer(stream=stream, frame_callback=_decorate)

    with player:
        player.autoplay()
