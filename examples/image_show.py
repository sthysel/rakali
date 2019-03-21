#! /usr/bin/env python

from rakali.testimages import orb_spider, rakali

for image in (orb_spider, rakali):
    image.info()
    image.show()
