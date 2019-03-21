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
def canny(img):
    img = imutils.auto_canny(image=img, sigma=0.3)
    img = add_frame_labels(
        frame=img,
        labels=[
            f'canny cost: {canny.cost:6.3f}s',
            'q to quit',
        ],
        color=colors.get('WHITE'),
    )
    return img


stream = VideoStream(src=0)
writer = VideoWriter(
    size=stream.get_wh_size(),
    file_name='canny.avi',
    color=False,
    fps=60,
)
player = VideoPlayer()

with stream, player, writer:
    while go():
        ok, frame = stream.read()
        if ok:
            frame = canny(frame)
            writer.write(frame)
            player.show(frame)
