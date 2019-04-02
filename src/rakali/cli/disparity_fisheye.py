""" Show disparity map for rectified stereo fish eye images """

import sys
from pathlib import Path

import click
import cv2 as cv
import numpy as np

from rakali.annotate import add_frame_labels, colors
from rakali.camera.fisheye_stereo import CalibratedStereoFisheyeCamera, calibration_labels
from rakali import transforms


@click.command(context_settings=dict(max_content_width=120))
@click.version_option()
@click.argument(
    'image_number',
)
@click.option(
    '--chessboards-folder',
    help='Chessboard images store folder',
    default='~/rakali/stereo/chessboards/',
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
def cli(image_number, chessboards_folder, calibration_file, balance, scale):
    """
    Load stereo fisheye images, correct them and display the disparity map
    """

    # get matching pair of images from folder
    left_frame, right_frame = get_frames(chessboards_folder, image_number)

    # get calibrated stereo rig
    camera = CalibratedStereoFisheyeCamera(
        calibration_file=calibration_file,
        balance=balance,
        dim2=None,
        dim3=None,  # remember we have these
    )

    # set correction maps
    camera.set_maps(left_frame)

    # unwarp pair images
    rectified = camera.correct(left_frame, right_frame)

    # add calibration info
    left_frame = add_calib_info(camera, left_frame, 'left')
    right_frame = add_calib_info(camera, right_frame, 'right')

    # display them
    original = np.hstack((left_frame, right_frame))
    corrected = np.hstack(rectified)
    quad = transforms.scale(np.vstack((original, corrected)), scale)
    cv.imshow('Original and corrected', quad)

    # stereo = cv.StereoBM_create(numDisparities=16 * 4, blockSize=15)
    cv.namedWindow('disparity')

    tuner = DisparityTuner(rectified, camera)
    tuner.refresh()
    while True:
        if cv.waitKey(1) & 0xFF == ord('q'):
            break


class DisparityTuner:
    def __init__(self, pair, camera):
        self.rectified_pair = pair
        self.camera = camera

        self.window_size = 8
        self.min_disp = 16
        self.block_size = 16
        self.num_disp = 112 - self.min_disp
        self.disp12_max_diff = 1
        self.uniqueness = 10
        self.speckle_size = 100
        self.speckle_range = 32

        cv.createTrackbar('Window Size', 'disparity', self.window_size, 15, self.on_window_size)
        cv.createTrackbar('Minimum Disparity ', 'disparity', self.min_disp, 16 * 5, self.on_min_disparity)
        cv.createTrackbar('Max diff ', 'disparity', self.disp12_max_diff, 200, self.on_max_diff)
        cv.createTrackbar('Uniqueness', 'disparity', self.uniqueness, 100, self.on_uniqueness)
        cv.createTrackbar('Speckle Size', 'disparity', self.speckle_size, 1000, self.on_speckle_size)
        cv.createTrackbar('Speckle Range', 'disparity', self.speckle_range, 1000, self.on_speckle_range)
        cv.createTrackbar('Block Size', 'disparity', self.block_size, 30, self.on_block_size)

    def on_min_disparity(self, val):
        if val % 16 == 0:
            self.min_disp = val
            self.num_disp = 112 - self.min_disp
            self.refresh()

    def on_block_size(self, val):
        self.block_size = val
        self.refresh()

    def on_window_size(self, val):
        self.window_size = val
        self.refresh()

    def on_uniqueness(self, val):
        self.uniqueness = val
        self.refresh()

    def on_speckle_size(self, val):
        self.speckle_size = val
        self.refresh()

    def on_speckle_range(self, val):
        self.speckle_range = val
        self.refresh()

    def on_max_diff(self, val):
        self.disp12_max_diff = val
        self.refresh()

    def refresh(self):
        stereo = cv.StereoSGBM_create(
            minDisparity=self.min_disp,
            numDisparities=self.num_disp,
            blockSize=self.block_size,
            P1=8 * 3 * self.window_size**2,
            P2=32 * 3 * self.window_size**2,
            disp12MaxDiff=self.disp12_max_diff,
            uniquenessRatio=self.uniqueness,
            speckleWindowSize=self.speckle_size,
            speckleRange=self.speckle_range,
        )

        l, r = self.rectified_pair
        l = cv.pyrDown(cv.cvtColor(l, cv.COLOR_BGR2GRAY))
        r = cv.pyrDown(cv.cvtColor(r, cv.COLOR_BGR2GRAY))
        disp = stereo.compute(l, r).astype(np.float32) / 16.0
        cv.imshow('disparity', (disp - self.min_disp) / self.num_disp)


def get_frames(chessboards_folder, image_number):
    """get stereo frame pair from chessboard capture folder"""

    frames = []
    source = Path(chessboards_folder).expanduser()
    if not source.exists():
        print(f'Source folder {chessboards_folder} does not exist')
        sys.exit()

    for side in ('left', 'right'):
        fname = f'{side}_{image_number}.jpg'
        file_path = source / Path(fname)
        print(f'loading {file_path}')
        if not file_path.exists():
            print(f'{side} image file {file_path} does not exist')
            sys.exit()
        img = cv.imread(str(file_path))
        img = add_frame_labels(img, labels=[f'{file_path}'])
        img = add_reticle(img)
        frames.append(img)
    return frames


def add_calib_info(camera, img, side):
    """label the corrected frames to aid in diagnostics """

    return add_frame_labels(
        frame=img,
        labels=calibration_labels(camera.calibration, side),
        color=colors.get('BLACK'),
    )


def add_reticle(img):
    """ adds markup to frame for warp debug"""

    olive = colors.get('OLIVE')
    h, w = img.shape[:2]
    cx, cy = (int(w / 2), int(h / 2))
    center = cx, cy
    # circles
    for r in range(50, 300, 100):
        cv.circle(img=img, center=center, radius=r, lineType=cv.LINE_8, color=olive, thickness=1)

    # space
    for y in range(0, h, int(h / 20)):
        cv.line(img=img, pt1=(0, y), pt2=(w, y), color=olive, lineType=cv.LINE_4, thickness=1)
        if y == cy:
            cv.line(img=img, pt1=(0, y), pt2=(w, y), color=olive, lineType=cv.LINE_4, thickness=3)

    for x in range(0, w, int(w / 20)):
        cv.line(img=img, pt1=(x, 0), pt2=(x, h), color=olive, lineType=cv.LINE_4, thickness=1)
        if x == cx:
            cv.line(img=img, pt1=(x, 0), pt2=(x, h), color=olive, lineType=cv.LINE_4, thickness=3)

    return img


def label_frame(camera, frame):
    labels = [
        f'Reprojected fisheye frame',
        f'undistort cost: {camera.correct.cost:6.3f}s',
        f'balance: {camera.balance}',
        f'cid: {camera.cid} calibrated on {camera.calibration_time_formatted}',
        # f'dim2 {dim2}',
        # f'dim3 {dim3}',
    ]
    labeled_frame = add_frame_labels(
        frame=frame,
        labels=labels,
        color=colors.get('BHP'),
    )
    return labeled_frame
