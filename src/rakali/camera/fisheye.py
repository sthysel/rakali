"""
Fisheye camera support
"""

import cv2 as cv
import numpy as np
from rakali.video.fps import cost


def save_calibration(
    calibration_file,
    K,
    D,
    image_size,
    salt: int,
    pick_size: int,
    error: float,
):
    """Save fisheye calibation to file"""

    print(f'Saving fisheye calibration data to {calibration_file}')
    np.savez_compressed(
        calibration_file,
        K=K,
        D=D,
        image_size=image_size,
        salt=salt,
        pick_size=pick_size,
        error=error,
    )


def load_calibration(calibration_file):
    """Load fisheye calibration data from file"""

    print(f'Loading fisheye calibration data from {calibration_file}')
    cal = np.load(calibration_file)
    return dict(
        K=cal['K'],
        D=cal['D'],
        image_size=cal['image_size'],
        salt=int(cal['salt']),
        pick_size=int(cal['pick_size']),
        error=float(cal['error']),
    )


def get_maps(
    img,
    calibration_dim,
    K,
    D,
    balance: float = 0.5,
    dim2=None,
    dim3=None,
):
    """calculate fish-eye reprojection maps"""

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
    new_K = cv.fisheye.estimateNewCameraMatrixForUndistortRectify(
        K=scaled_K,
        D=D,
        image_size=dim2,
        R=np.eye(3),
        balance=balance,
    )
    map1, map2 = cv.fisheye.initUndistortRectifyMap(
        K=scaled_K,
        D=D,
        R=np.eye(3),
        P=new_K,
        size=dim3,
        m1type=cv.CV_16SC2,
    )
    return map1, map2


@cost
def undistort(img, map1, map2):
    """undistort fisheye image"""

    undistorted_img = cv.remap(
        src=img,
        map1=map1,
        map2=map2,
        interpolation=cv.INTER_LINEAR,
        borderMode=cv.BORDER_CONSTANT,
    )

    return undistorted_img
