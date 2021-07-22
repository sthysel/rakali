# Rakali (Version 0.0.10)

Rakali is a imaging library and video camera tool-set. It provides a number of
camera primitives to help with calibrating mono and stereo camera rigs, image
processing and object detection. It also includes a number of pre-built tools to
help with that.

Rakali makes use of many other imaging libraries and frameworks and is also intended
to be used as a pedagogical resource for those.

![Rakali by Pia Ravenari](https://raw.githubusercontent.com/sthysel/rakali/master/docs/pics/rakali.jpg)

[Pia Ravenari](https://www.deviantart.com/ravenari)

Named after Hydromys chrysogaster, the Australian Otter

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/sthysel/rakali/master.svg)](https://results.pre-commit.ci/latest/github/sthysel/rakali/master)

# Provided tools

Rakali ships with a number of tools that assists working with mono and stereo
video cameras.


| Tool                            | Purpose                                                        |
| ---                             | ---                                                            |
| rakali-find-ipcameras           | Discover IP cameras on the local LAN                           |
| rakali-view                     | View live video stream                                         |
| rakali-view-stereo              | View live stereo video stream                                  |
| rakali-find-chessboards         | Find calibration images in live video feed                     |
| rakali-find-chessboards-stereo  | Find calibration images in live stereo video feed              |
| rakali-calibrate-pinhole        | Calibrate a standard lens camera                               |
| rakali-calibrate-fisheye        | Calibrate a fish-eyed lens camera                              |
| rakali-calibrate-fisheye-stereo | Calibrate a fish-eyed stereo rig                               |
| rakali-undistort-pinhole        | Correct standard lens camera live video feed                   |
| rakali-undistort-fisheye        | Correct fish-eye camera live video feed                        |
| rakali-undistort-fisheye-image  | Correct image provided by calibrated fish-eye camera           |
| rakali-split-stereo-feed        | Split recorded stereo view feeds into left and right eye views |
| rakali                          | Image processing library examplar                              |


## rakali-find-ipcameras

Scan local LAN for IP cameras by vendor and service.

`$ rakali-find-ipcameras cams`

```
Usage: rakali-find-ipcameras [OPTIONS] COMMAND [ARGS]...

  Discover IP cameras on local LAN

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  cams     Discover local IP cameras using vendor name
  service  Scanning for video feed services
```

To scan for cameras, do: `$ rakali-find-ipcameras cams`, the default is to search for axis models.

Which provides a list of discovered NVR's or cameras like so:

```
Scanning 10.41.212.0/24 for axis cameras or NVRs
['10.41.212.135', '10.41.212.147']
```


## rakali-view

View live video feed from IP and USB cameras. IP cameras and NVR's that
broadcast their services over mDNS can be discovered using
`rakali-find-ipcameras`.

`$ rakali-view --help`

```
Usage: rakali-view [OPTIONS]

Options:
  --version          Show the version and exit.
  -s, --source TEXT  Video source, can be local USB cam (0|1|2..) or IP cam rtsp URL or file  [default: http://axis-
                     lab/axis-cgi/mjpg/video.cgi?&camera=2]
  --help             Show this message and exit.
```

A simple single stream video player.

![View](docs/pics/rakali-view.jpg)

## rakali-find-chessboards

![View](docs/pics/chessboard.jpg)

Find checkerboard images in video feed for calibration purposes.

`rakali-find-chessboards` will look for a chessboard patterns in the frame flow
and save each frame containing a chessboard for batch processing during camera
calibration.

`$ rakali-find-chessboards --help`

```zsh

Usage: rakali-find-chessboards [OPTIONS]

  Test each frame in the stream for the presence of a chess-board pattern. If found, save to the output folder

Options:
  --version                     Show the version and exit.
  -s, --source TEXT             Video source, can be local USB cam (0|1|2..) or IP cam rtsp URL or file  [default:
                                http://axis-lab/axis-cgi/mjpg/video.cgi?&camera=1]
  -o, --output-folder TEXT      Output folder for images containing a chessboard  [default: ~/rakali/chessboards/]
  --chessboard-rows INTEGER     Chessboard rows  [default: 9]
  --chessboard-columns INTEGER  Chessboard columns  [default: 6]
  --help                        Show this message and exit.

```

The process will drop calibration frames in the target folder like these:

```
$ tree ~/rakali/chessboards
/home/thys/rakali/chessboards
├── 00000.jpg
├── 00001.jpg
├── 00002.jpg
├── 00003.jpg
```


## rakali-find-chessboards-stereo


Find checkerboard images in stereo video feed for calibration purposes. It
operates in the same way as `rakali-find-chessboards` but produces pairs of
frames.

`rakali-find-chessboards-stereo --help`

```
Usage: rakali-find-chessboards-stereo [OPTIONS]

  Find chessboard calibration images in both frames of the stereo pair

Options:
  --version                     Show the version and exit.
  -l, --left-eye TEXT           Left eye, can be local USB cam (0|1|2..) or IP cam rtsp URL or file  [default:
                                http://axis-lab/axis-cgi/mjpg/video.cgi?&camera=1]
  -r, --right-eye TEXT          Right eye, can be local USB cam (0|1|2..) or IP cam rtsp URL or file  [default:
                                http://axis-lab/axis-cgi/mjpg/video.cgi?&camera=2]
  -o, --output-folder TEXT      Fetch image from URL  [default: ~/rakali/stereo/chessboards/]
  --chessboard-rows INTEGER     Chessboard rows  [default: 9]
  --chessboard-columns INTEGER  Chessboard columns  [default: 6]
  --help                        Show this message and exit.
```

![View](docs/pics/stereo-chessboard.jpg)


``` zsh
$ tree ~/rakali/stereo/chessboards
/home/thys/rakali/stereo/chessboards
├── left_00000.jpg
├── left_00001.jpg
├── left_00002.jpg
├── right_00000.jpg
├── right_00001.jpg
├── right_00002.jpg

```


## rakali-calibrate-pinhole

Calibrate a video camera with a pinhole lens

`$ rakali-calibrate-pinhole --help `

```
Usage: rakali-calibrate-pinhole [OPTIONS]

  Calibrate pinhole camera using chessboard frames captured earlier.

Options:
  --version                     Show the version and exit.
  -i, --input-folder TEXT       Folder where chessboard images are stored  [default: ~/rakali/chessboards/]
  --image-points-file TEXT      Corner points data  [default: image_points.npz]
  --calibration-file TEXT       Camera calibration data  [default: pinhole_calibration.npz]
  --chessboard-rows INTEGER     Chessboard rows  [default: 9]
  --chessboard-columns INTEGER  Chessboard columns  [default: 6]
  --square-size FLOAT           Chessboard square size in m  [default: 0.023]
  --salt INTEGER                Seed value for random picking of calibration images from a large set  [default: 888]
  --pick-size INTEGER           Size of image set to use for calibration, picked from available set  [default: 50]
  --help                        Show this message and exit.
```


## rakali-calibrate-fisheye

Calibrate a video camera with a fish-eye lens using chessboard calibration
images captured using `rakali-find-chessboards`.

`$ rakali-calibrate-fisheye --help`

```
Usage: rakali-calibrate-fisheye [OPTIONS]

  Calibrate fish-eye camera using chessboard frames captured earlier.

Options:
  --version                     Show the version and exit.
  -i, --input-folder TEXT       Folder where chessboard images are stored  [default: ~/rakali/chessboards/]
  --image-points-file TEXT      Corner points data  [default: image_points.npz]
  --calibration-file TEXT       Camera calibration data  [default: fisheye_calibration.npz]
  --chessboard-rows INTEGER     Chessboard rows  [default: 9]
  --chessboard-columns INTEGER  Chessboard columns  [default: 6]
  --square-size FLOAT           Chessboard square size in m  [default: 0.023]
  --salt INTEGER                Seed value for random picking of calibration images from a large set  [default: 888]
  --pick-size INTEGER           Size of image set to use for calibration, picked from available set  [default: 50]
  --cid TEXT                    Calibration ID to associate a calibration file with a device  [default: fisheye]
  --help                        Show this message and exit.

```


Executing `$ rakali-calibrate-fisheye` results:

```
$ rakali-calibrate-fisheye
Loading previously computed image points from image_points.npz
Calibrating on 50 objects...
INFO:rakali.camera.fisheye:Saving fisheye calibration data to fisheye_calibration.npz
DIM=(1920, 1080)
K=np.array([[558.6421513930135, 0.0, 977.0871045041308], [0.0, 559.5579191046008, 493.7827965652395], [0.0, 0.0, 1.0]])
D=np.array([[-0.018316232894576033], [0.002931049514785237], [-0.0022823146847841804], [0.00014813140230995043]])
Calibration error: 0.8771782112164381
```

The resulting calibration file contains the K and D matrixes and some metadata

```json
{
    "D": [
        [
            -0.018316232894576033
        ],
        [
            0.002931049514785237
        ],
        [
            -0.0022823146847841804
        ],
        [
            0.00014813140230995043
        ]
    ],
    "K": [
        [
            558.6421513930135,
            0.0,
            977.0871045041308
        ],
        [
            0.0,
            559.5579191046008,
            493.7827965652395
        ],
        [
            0.0,
            0.0,
            1.0
        ]
    ],
    "cid": "fisheye",
    "error": 0.8771782112164381,
    "image_size": [
        1920,
        1080
    ],
    "pick_size": 50,
    "salt": 888,
    "time": 1553647761.7596939
}
```

## rakali-calibrate-fisheye-stereo

`rakali-calibrate-fisheye-stereo` uses a fixed set of previously captured chessboard images to calibrate a
fisheye stereo camera rig. The calculated parameters are saved in a calibration file for use in image
rectification.

`$ rakali-calibrate-fisheye-stereo --help`

``` zsh
Usage: rakali-calibrate-fisheye-stereo [OPTIONS]

  Calibrate fish-eye stereo camera rig using chessboard frames captured earlier.

Options:
  --version                       Show the version and exit.
  -i, --input-folder TEXT         Folder where chessboard images are stored  [default: ~/rakali/stereo/chessboards/]
  --left-image-points-file TEXT   Left Corner points data  [default: left_image_points.json]
  --right-image-points-file TEXT  Right Corner points data  [default: right_image_points.json]
  --calibration-file TEXT         Stereo Camera calibration data  [default: fisheye_stereo_calibration.json]
  --chessboard-rows INTEGER       Chessboard rows  [default: 9]
  --chessboard-columns INTEGER    Chessboard columns  [default: 6]
  --square-size FLOAT             Chessboard square size in m  [default: 0.023]
  --salt INTEGER                  Seed value for random picking of calibration images from a large set  [default: 888]
  --pick-size INTEGER             Size of image set to use for calibration, picked from available set  [default: 50]
  --cid TEXT                      Calibration ID to associate a calibration file with a device  [default: fisheye]
  --prefilter / --no-prefilter    Prefilter images  [default: True]
  --help                          Show this message and exit.
```

```zsh
....
Image /home/thys/rakali/stereo/chessboards/left_00088.jpg OK
Image /home/thys/rakali/stereo/chessboards/left_00058.jpg OK
Image /home/thys/rakali/stereo/chessboards/right_00238.jpg OK
Image /home/thys/rakali/stereo/chessboards/left_00122.jpg OK
Loading previously computed image points from left_image_points.json
Calibrating on 50 objects...
Loading previously computed image points from right_image_points.json
Calibrating on 50 objects...
Calibrate Fisheye Stereo camera using pre-calibrated values
DIM=(1920, 1080)
left calibration
K=np.array([[552.7233750094179, 0.0, 948.2959591699556], [0.0, 554.6925141069631, 548.3575557665413], [0.0, 0.0, 1.0]])
D=np.array([[-0.05136306776237411], [0.0959513318929465], [-0.09081590588179426], [0.028414418435600244]])
Calibration error: 0.5128009096414867
right calibration
K=np.array([[552.7233750094177, 0.0, 948.2959591699567], [0.0, 554.6925141069636, 548.3575557665405], [0.0, 0.0, 1.0]])
D=np.array([[-0.051363067762376646], [0.09595133189294996], [-0.09081590588179408], [0.028414418435599085]])
Calibration error: 0.46991635076102695

```


## rakali-undistort-pinhole

Correct video feed from calibrated standard pinhole camera

`$ rakali-undistort-pinhole --help`

```
Usage: rakali-undistort-pinhole [OPTIONS]

  Undistort live feed from pinhole model type camera

Options:
  --version                Show the version and exit.
  -s, --source TEXT        Video source, can be local USB cam (0|1|2..) or IP cam rtsp URL or file  [default:
                           http://axis-lab/axis-cgi/mjpg/video.cgi?&camera=1]
  --calibration-file TEXT  Camera calibration data  [default: pinhole_calibration.npz]
  --help                   Show this message and exit.
```

## rakali-undistort-fisheye

Correct video feed from calibrated fisheye-lens camera

`$ rakali-undistort-fisheye --help`

```
Usage: rakali-undistort-fisheye [OPTIONS]

  Undistort live video feed from fish-eye lens camera

Options:
  --version                Show the version and exit.
  -s, --source TEXT        Video source, can be local USB cam (0|1|2..) or IP cam rtsp URL or file  [default:
                           http://axis-lab/axis-cgi/mjpg/video.cgi?&camera=1]
  --calibration-file PATH  Camera calibration data  [default: fisheye_calibration.npz]
  -b, --balance FLOAT      Balance value 0.0 ~30% pixel loss, 1.0 no loss  [default: 1.0]
  --help                   Show this message and exit.

```

`$ rakali-undistort-fisheye`

![View](docs/pics/fisheye-undistort-balance1.jpg)

`$ rakali-undistort-fisheye -b 0.5`

![View](docs/pics/fisheye-undistort-balance0.5.jpg)


`$ rakali-undistort-fisheye -b 0`

![View](docs/pics/fisheye-undistort-balance0.0.jpg)


## rakali-undistort-fisheye-image

`$ rakali-undistort-fisheye-image --help`

``` zsh
Usage: rakali-undistort-fisheye-image [OPTIONS] IMAGE_PATH

  Rectify a image taken with a fish-eye lens camera using calibration parameters

Options:
  --version                Show the version and exit.
  --calibration-file PATH  Camera calibration data  [default: fisheye_calibration.json; required]
  -b, --balance FLOAT      Balance value 0.0 ~30% pixel loss, 1.0 no loss  [default: 1.0]
  -s, --scale FLOAT        Scale image  [default: 0.5]
  --help                   Show this message and exit.
```

`$ rakali-undistort-fisheye-image ~/rakali/chessboards/00000.jpg`

![View](docs/pics/fisheye-undistort-file.jpg)


## rakali-view-stereo

View live feed from stereo camera rig

`$ rakali-view-stereo --help `

```
Usage: rakali-view-stereo [OPTIONS]

Options:
  --version             Show the version and exit.
  -l, --left-eye TEXT   Left eye, can be local USB cam (0|1|2..) or IP cam rtsp URL or file  [default: http://axis-
                        lab/axis-cgi/mjpg/video.cgi?&camera=1]
  -r, --right-eye TEXT  Right eye, can be local USB cam (0|1|2..) or IP cam rtsp URL or file  [default: http://axis-
                        lab/axis-cgi/mjpg/video.cgi?&camera=2]
  --help                Show this message and exit.

```

![Stereo View](docs/pics/stereo-view.jpg)

## rakali-split-stereo-feed

Split source stereo recording into left and right camera views

`$ rakali-split-stereo-feed --help`

```
Usage: rakali-split-stereo-feed [OPTIONS]

  Split source stereo recording into left and right camera views

Options:
  --version              Show the version and exit.
  -s, --source TEXT      Stereo video source file to split  [default: in.avi]
  -l, --left-name TEXT   Left camera video name  [default: left_eye_out.avi]
  -r, --right-name TEXT  Right camera video name  [default: right_eye_out.avi]
  --fps FLOAT            Frames per second rate for output file  [default: 12.5]
  --help                 Show this message and exit.
```


## rakali

Rakali ships with a small demo app that exercises the library image processing
functionality.

```zsh
$ rakali --help
Usage: rakali [OPTIONS] COMMAND [ARGS]...

  Rakali image tools

  Provide either a input file or a input URL for image source

Options:
  --version               Show the version and exit.
  -i, --input-file PATH   Use file
  -u, --input-url TEXT    Fetch image from URL
  -o, --output-file PATH  Output file  [default: out.jpg]
  --help                  Show this message and exit.

Commands:
  resize          Resize the input image preserving aspect ratio, favoring width
  rotate          Rotate the input image
  rotate-bounded  Rotate the input image, keeping bound in place
  skeletonize     Skeletonize the input image

```

# Library usage

Library documentation generation is a work in progress...

## Load and show image from file

```zsh
from rakali import Image
Image.from_file('rakali.jpg').show()
```

## Load, annotate, and show image

```zsh
#! /usr/bin/env python

from rakali import Image
img: Image = Image.from_file('rakali.jpg')
img.add_text(labels=['Rakali', 'Hydromys chrysogaster'])
img.show()
img.write('rakali-text.jpg')

```

![Text](https://raw.githubusercontent.com/sthysel/rakali/master/docs/pics/rakali-text.jpg)

## Canny

```zsh

#! /usr/bin/env python
"""
Cannyfy Live USB video stream
"""

from rakali import VideoPlayer, VideoStream, VideoWriter
from rakali.video.fps import cost
from rakali.video import go
from rakali.annotate import add_frame_labels, colors
import imutils
import logging

logging.basicConfig(level=logging.DEBUG)


@cost
def canny(mat):
    img = imutils.auto_canny(image=mat, sigma=0.3)
    img = add_frame_labels(
        frame=img,
        labels=[f'canny cost: {canny.cost:6.3f}ms'],
        color=colors.get('WHITE'),
    )
    return img


stream = VideoStream(src=0)
player = VideoPlayer()
writer = VideoWriter(size=stream.get_wh_size(), file_name='canny.avi')

with stream, player, writer:
    while go():
        frame = canny(stream.read())
        writer.write(frame)
        player.show(frame)
```

![canny](docs/pics/canny.jpg)



# Install

Rakali is essentially a OpenCV shim. Because some parts of Rakali depends on OpenCV CUDA being available. The
'python-opencv' lib on PyPi is not marked as a dependency. You need to install either that yourself, or use
your own pre-compiled OpenCV CUDA. Arch Linux has opencv-cuda in AUR, so install that:

```
$ yay -S opencv-cuda
```

While you are at it also install `tensorflow-opt-cuda`:

```
# pacman -S tensorflow-opt-cuda
```


## pypi

Rakali is in pypi:

```
$ pip install rakali
```

## Manual install

Clone or download this repo and in your virtualenv do:
```
$ pip install .
```
