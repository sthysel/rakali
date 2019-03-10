#! /usr/bin/env python

from rakali import VideoPlayer, VideoStream
import imutils

FRONT_LAWN = 1
WATER_HEATER = 2
PARK = 3
BACK_LAWN = 4

SOURCE = f'rtsp://10.0.0.247:554/ch0{PARK}/01'


def canny(mat):
    return imutils.auto_canny(image=mat, sigma=0.3)


stream = VideoStream(src=SOURCE)
player = VideoPlayer(stream=stream, frame_callback=canny)

with player:
    player.play()
