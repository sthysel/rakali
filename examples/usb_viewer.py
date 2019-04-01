#! /usr/bin/env python

from rakali import VideoPlayer, VideoStream

stream = VideoStream(src=5)
player = VideoPlayer(stream=stream)

with player:
    player.autoplay()
