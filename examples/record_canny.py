#! /usr/bin/env python
import cv2 as cv
from rakali import VideoPlayer, VideoStream, VideoWriter
from rakali.video.fps import cost
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
    while cv.waitKey(1) & 0xFF != ord('q'):
        frame = canny(stream.read())
        writer.write(frame)
        player.show(frame)
