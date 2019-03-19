import cv2
import numpy as np
import sys

DIM = (1920, 1080)
K = np.array([[567.3170670993122, 0.0, 976.0120777004776],
              [0.0, 565.0311669847642, 474.9942585301562], [0.0, 0.0, 1.0]])
D = np.array([[-0.05503152854179671], [0.045691961267593166],
              [-0.02707027623305218], [0.005637830698947465]])


def undistort(img_path):
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


def undistort(img_path, balance=0.5, dim2=None, dim3=None):
    img = cv2.imread(img_path)

    #dim1 is the dimension of input image to un-distort
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

    # This is how scaled_K, dim2 and balance are used to determine the final K used to un-distort image. OpenCV document failed to make this clear!
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

    cc = np.hstack((img, undistorted_img))
    cv2.imshow("undistorted", cc)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    for p in sys.argv[1:]:
        undistort(p)
