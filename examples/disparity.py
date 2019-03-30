import numpy as np
import cv2 as cv

imgL = cv.pyrDown(cv.imread('left_00000.jpg', 0))
imgR = cv.pyrDown(cv.imread('right_00000.jpg', 0))

window_size = 3
min_disp = 16
num_disp = 112 - min_disp
stereo = cv.StereoSGBM_create(
    minDisparity=min_disp,
    numDisparities=num_disp,
    blockSize=16,
    P1=8 * 3 * window_size**2,
    P2=32 * 3 * window_size**2,
    disp12MaxDiff=1,
    uniquenessRatio=20,
    speckleWindowSize=100,
    speckleRange=32,
)

print('computing disparity...')
disp = stereo.compute(imgL, imgR).astype(np.float32) / 16.0

cv.imshow('left', imgL)
cv.imshow('right', imgR)
cv.imshow('disparity', (disp - min_disp) / num_disp)

while True:
    import sys
    if cv.waitKey(1) & 0xFF == ord('q'):
        cv.destroyAllWindows()
        sys.exit()
