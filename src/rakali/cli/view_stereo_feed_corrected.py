""" View corrected stereo feed """

import logging
import sys

import click
import numpy as np

from rakali import VideoPlayer
from rakali.annotate import add_frame_labels, colors
from rakali.camera.fisheye_stereo import CalibratedStereoFisheyeCamera, calibration_labels
from rakali.stereo.reader import StereoCamera
from rakali.video import go

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
def cli(left_eye, right_eye, calibration_file, balance, scale):
    """
    Show corrected stereo camera feeds
    """
    stream = StereoCamera(
        left_src=left_eye,
        right_src=right_eye,
    )

    # get calibrated stereo rig
    camera = CalibratedStereoFisheyeCamera(
        calibration_file=calibration_file,
        balance=balance,
        dim2=None,
        dim3=None,  # remember we have these
    )

    # label the corrected frames to aid in diagnostics
    calibration_labels_per_side = dict(
        left=calibration_labels(camera.calibration, 'left'),
        right=calibration_labels(camera.calibration, 'right'),
    )

    # set correction maps
    ok, frames = stream.read()
    if ok:
        camera.set_maps(frames.frames()[0])
    else:
        print('Error reading from stereo video stream')
        sys.exit()

    player = VideoPlayer(scale=scale)

    with player, stream:
        count = 0
        while go():
            ok, frames = stream.read()
            if ok:
                count += 1
                annotated = []
                annotated_rectified = []
                left, right = frames.frames()
                # unwarp pair images
                rectified = camera.correct(left, right)
                for side, source, frame, corrected_frame in zip(
                    ('left', 'right'),
                    (left_eye, right_eye),
                    (left, right),
                    rectified,
                ):
                    annotated.append(decorate_frame(
                        frame=frame,
                        side=side,
                        count=count,
                        source=source,
                    ))
                    # label corrected frame
                    annotated_rectified.append(
                        add_frame_labels(
                            frame=corrected_frame,
                            labels=calibration_labels_per_side[side],
                            color=colors.get('BLACK'),
                        )
                    )

                orig = np.hstack(annotated)
                corrected = np.hstack(annotated_rectified)
                stack = np.vstack((orig, corrected))
                player.show(stack)


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
