#! /usr/bin/env python
"""
Reads rtsp stream from IP camera, applies canny edge detection to each frame
and displays it
"""

import imutils
from rakali import VideoPlayer, VideoStream
from rakali.annotate import add_frame_labels, colors
from rakali.video.fps import cost

FRONT_LAWN = 1
WATER_HEATER = 2
PARK = 3
BACK_LAWN = 4

SOURCE = f"rtsp://10.0.0.247:554/ch0{WATER_HEATER}/01"
# SOURCE = f'rtsp://10.41.212.133/axis-media/media.amp?camera=2'


@cost
def canny(mat):
    img = imutils.auto_canny(image=mat, sigma=0.3)
    img = add_frame_labels(
        frame=img,
        labels=[
            f"canny cost: {canny.cost:6.3f}s",
            "q to quit",
        ],
        color=colors.get("WHITE"),
    )
    return img


stream = VideoStream(src=SOURCE)
player = VideoPlayer(stream=stream, frame_callback=canny)

with player:
    player.autoplay()
