import click
import numpy as np

from rakali import VideoPlayer
from rakali.video import VideoFile, go, VideoStream
from rakali.annotate import add_frame_labels, colors
from rakali.camera.fisheye import CalibratedFisheyeCamera

import sys


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
    default='fisheye_calibration.npz',
    type=click.Path(exists=True),
    show_default=True,
)
@click.option(
    '-b',
    '--balance',
    help='Balance value 0.0 ~30% pixel loss, 1.0 no loss',
    default=1.0,
    show_default=True,
)
def cli(source, calibration_file, balance):
    """
    Undistort live video feed from fish-eye lens camera
    """

    camera = CalibratedFisheyeCamera(
        calibration_file=calibration_file,
        balance=balance,
        dim2=None,
        dim3=None,  # remember we have these
    )
    stream = VideoStream(src=source)
    player = VideoPlayer()

    with stream, player:
        ok, frame = stream.read()
        if ok:
            camera.set_map(first_frame=frame)
        else:
            print('Cannot read video feed')
            sys.exit(0)

        frame_count = 0
        while go():
            ok, frame = stream.read()
            if ok:
                frame_count += 1
                undistorted_frame = camera.correct(frame)
                labels = [
                    f'Reprojected fisheye frame: {frame_count}',
                    f'undistort cost: {camera.correct.cost:6.3f}s',
                    f'balance: {balance}',
                    f'cid: {camera.cid} calibrated on {camera.calibration_time_formatted}',
                    # f'dim2 {dim2}',
                    # f'dim3 {dim3}',
                ]
                labeled_frame = add_frame_labels(
                    frame=undistorted_frame,
                    labels=labels,
                    color=colors.get('BHP'),
                )
                stack = np.hstack((frame, labeled_frame))
                player.show(stack)
