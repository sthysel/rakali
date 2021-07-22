#! /usr/bin/env python

import imutils
from rakali import VideoPlayer, VideoStream
from rakali.annotate import add_frame_labels, colors
from rakali.video.fps import cost


@cost
def canny(mat):
    img = imutils.auto_canny(image=mat, sigma=0.3)
    img = add_frame_labels(
        frame=img,
        labels=[f"canny cost: {canny.cost:6.3f}s"],
        color=colors.get("WHITE"),
    )
    return img


stream = VideoStream(src=0)
player = VideoPlayer(stream=stream, frame_callback=canny)

with player:
    player.autoplay()
