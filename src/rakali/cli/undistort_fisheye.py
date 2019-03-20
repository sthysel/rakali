import click
import cv2
import numpy as np

from rakali import VideoPlayer
from rakali.video import VideoFile, go
from rakali.video.fps import cost
from rakali.annotate import add_frame_labels, colors

DIM = (1920, 1080)
K = np.array(
    [[567.3170670993122, 0.0, 976.0120777004776], [0.0, 565.0311669847642, 474.9942585301562], [0.0, 0.0, 1.0]]
)
D = np.array([[-0.05503152854179671], [0.045691961267593166], [-0.02707027623305218], [0.005637830698947465]])


def simple_undistort(img_path):
    """
    Undistorts with 30% pixel loss.
    """
    img = cv2.imread(img_path)
    h, w = img.shape[:2]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(
        K,
        D,
        np.eye(3),
        K,
        DIM,
        cv2.CV_16SC2,
    )
    undistorted_img = cv2.remap(
        img,
        map1,
        map2,
        interpolation=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
    )

    cc = np.hstack((img, undistorted_img))
    cv2.imshow("undistorted", cc)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


@cost
def undistort(img, balance=0.5, dim2=None, dim3=None):
    """undistort fisheye image"""

    dim1 = img.shape[:2][::-1]
    assert dim1[0] / dim1[1] == DIM[0] / DIM[
        1], "Image to undistort needs to have same aspect ratio as the ones used in calibration"

    if not dim2:
        dim2 = dim1
    if not dim3:
        dim3 = dim1
    # The values of K is to scale with image dimension.
    scaled_K = K * dim1[0] / DIM[0]
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
    undistorted_img = cv2.remap(
        img,
        map1,
        map2,
        interpolation=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
    )

    labels = [
        f'undistort cost: {undistort.cost:6.3f}ms',
        f'balance {balance}',
        f'dim2 {dim2}',
        f'dim3 {dim3}',
    ]
    labeled_image = add_frame_labels(
        frame=undistorted_img,
        labels=labels,
        color=colors.get('BHP'),
    )

    return np.hstack((img, labeled_image))


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
def cli(source, calibration_file):
    """
    Undistort live video feed from fish-eye lens camera
    """

    stream = VideoFile(src=str(source))
    player = VideoPlayer()

    with stream, player:
        while go():
            ok, frame = stream.read()
            if ok:
                player.show(undistort(img=frame))
