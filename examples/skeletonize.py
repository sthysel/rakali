#! /usr/bin/env python

from pathlib import Path

from rakali import Image

img: Image = Image.from_file(Path("rakali.jpg"))
img.skeletonize()
img.show()
img.write("rakali-skeletonize.jpg")
