#! /usr/bin/env python

from rakali import VideoPlayer, VideoStream
from rakali.annotate import add_frame_labels, colors

FRONT_LAWN = 1
WATER_HEATER = 2
PARK = 3
BACK_LAWN = 4

SOURCE = f'rtsp://10.0.0.247:554/ch0{WATER_HEATER}/01'


def size(img):
    h, w = img.shape[:2]
    img = add_frame_labels(
        frame=img,
        labels=[
            f'size: {w}x{h}',
            'Geyser watch',
            'q to quit',
        ],
        color=colors.get('GREEN'),
    )
    return img


stream = VideoStream(src=SOURCE)
player = VideoPlayer(stream=stream, frame_callback=size)

with player:
    player.autoplay()
