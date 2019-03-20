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
    salt,
    pick_size,
    error,
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
    """Load fisheye calibration data"""

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


def xxxxundistort(img, balance=0.5, dim2=None, dim3=None):
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
    new_K = cv.fisheye.estimateNewCameraMatrixForUndistortRectify(
        scaled_K,
        D,
        dim2,
        np.eye(3),
        balance=balance,
    )
    map1, map2 = cv.fisheye.initUndistortRectifyMap(
        scaled_K,
        D,
        np.eye(3),
        new_K,
        dim3,
        cv.CV_16SC2,
    )
    undistorted_img = cv.remap(
        img,
        map1,
        map2,
        interpolation=cv.INTER_LINEAR,
        borderMode=cv.BORDER_CONSTANT,
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


class CorrectFishEye:
    def __init__(
        self,
        image_size,
        balance=1.0,
        dim2=None,
        dim3=None,
    ):
        self.image_size = image_size
        self.balance = balance
        self.dim2 = dim2
        self.dim3 = dim3

    def remap(self):
        """ calculate remap matrix"""

        dim1 = self.image_size
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
        new_K = cv.fisheye.estimateNewCameraMatrixForUndistortRectify(
            scaled_K,
            D,
            dim2,
            np.eye(3),
            balance=balance,
        )
        map1, map2 = cv.fisheye.initUndistortRectifyMap(
            scaled_K,
            D,
            np.eye(3),
            new_K,
            dim3,
            cv.CV_16SC2,
        )
        return map1, map2

    @cost
    def undistort(img, map1, map2):
        """undistort fisheye image"""

        undistorted_img = cv.remap(
            img,
            map1,
            map2,
            interpolation=cv.INTER_LINEAR,
            borderMode=cv.BORDER_CONSTANT,
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
