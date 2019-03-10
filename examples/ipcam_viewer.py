#! /usr/bin/env python

from rakali import VideoPlayer, VideoStream

FRONT_LAWN = 1
WATER_HEATER = 2
PARK = 3
BACK_LAWN = 4

SOURCE = f'rtsp://10.0.0.247:554/ch0{WATER_HEATER}/01'

stream = VideoStream(src=SOURCE)
player = VideoPlayer(stream=stream)

with player:
    player.autoplay()
