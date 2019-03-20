import click
import cv2
import numpy as np

from rakali import VideoPlayer
from rakali.video import VideoFile, go
from rakali.video.fps import cost
from rakali.annotate import add_frame_labels, colors

from rakali.camera.fisheye import load_calibration


def get_maps(
    img,
    calibration_dim,
    K,
    D,
    balance=0.5,
    dim2=None,
    dim3=None,
):
    """ calculate fish-eye reprojection maps"""

    dim1 = img.shape[:2][::-1]
    assert dim1[0] / dim1[1] == calibration_dim[0] / calibration_dim[
        1], "Image to undistort needs to have same aspect ratio as the ones used in calibration"

    if not dim2:
        dim2 = dim1
    if not dim3:
        dim3 = dim1
    # The values of K is to scale with image dimension.
    scaled_K = K * dim1[0] / calibration_dim[0]
    scaled_K[2][2] = 1.0  # Except that K[2][2] is always 1.0

    # use scaled_K, dim2 and balance to determine the final K used to un-distort image
    new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(
        scaled_K,
        D,
        dim2,
        np.eye(3),
        balance=balance,
    )
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(
        scaled_K,
        D,
        np.eye(3),
        new_K,
        dim3,
        cv2.CV_16SC2,
    )
    return map1, map2


@cost
def undistort(img, map1, map2):
    """undistort fisheye image"""

    undistorted_img = cv2.remap(
        img,
        map1,
        map2,
        interpolation=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
    )

    return undistorted_img


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
    calibration = load_calibration(calibration_file=calibration_file)
    calibration_dim = calibration['image_size']
    K = calibration['K']
    D = calibration['D']
    stream = VideoFile(src=str(source))
    player = VideoPlayer()

    with stream, player:
        _, frame = stream.read()
        map1, map2 = get_maps(
            frame,
            calibration_dim,
            K,
            D,
            balance,
            dim2=None,
            dim3=None,
        )
        frame_count = 0
        while go():
            ok, frame = stream.read()
            if ok:
                frame_count += 1
                undistorted_frame = undistort(img=frame, map1=map1, map2=map2)
                labels = [
                    f'Reprojected fisheye frame {frame_count}',
                    f'undistort cost: {undistort.cost:6.3f}ms',
                    f'balance {balance}',
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
