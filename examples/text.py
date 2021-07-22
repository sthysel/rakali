#! /usr/bin/env python

from pathlib import Path

from rakali import Image

img: Image = Image.from_file(Path("rakali.jpg"))
img.add_text(labels=["Rakali", "Hydromys chrysogaster"])
img.show()
img.write("rakali-text.jpg")
