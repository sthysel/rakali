#! /usr/bin/env python

from rakali import Image
img: Image = Image.from_file('rakali.jpg')
img.skeletonize()
img.show()
img.write('rakali-skeletonize.jpg')
