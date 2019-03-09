#! /usr/bin/env python

from rakali import Image
img = Image.from_file('rakali.jpg')
img.info()
img.show()
