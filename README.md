# Rakali (Version 0.0.7)

Rakali is a imaging library and tool-set. It makes use of many other imaging libraries and frameworks and is
also intended to be used as a pedagogical resource for those.

![Rakali by Pia Ravenari](https://raw.githubusercontent.com/sthysel/rakali/master/docs/pics/rakali.jpg)

[Pia Ravenari](https://www.deviantart.com/ravenari)

Named after Hydromys chrysogaster, the Australian Otter


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


# cli usage

Rakali ships with a small demo app that exercises the library functionality.

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

# Install

Rakali is essentially a OpenCV shim and installs the current (unofficial)
opencv-python wheel from PyPi. If you have a custom OpenCV build, make sure that
installing Rakali does not clobber that. 


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

