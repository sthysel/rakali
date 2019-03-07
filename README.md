# Rakali (Version 0.0.4)

Rakali is a imaging library and tool-set. It makes use of many other imaging libraries and frameworks and is
also intended to be used as a pedagogical resource for those.

![Rakali by Pia Ravenari](https://raw.githubusercontent.com/sthysel/rakali/master/docs/pics/rakali.jpg)

[Pia Ravenari](https://www.deviantart.com/ravenari)

Named after Hydromys chrysogaster, the Australian Otter


# Usage

## Load and show image from file

```zsh
from rakali import Image
Image.from_file('rakali.jpg').show()
```

# Install

Rakali is basically a OpenCV shim. Because many people use their own builds of OpenCV to enable CUDA or the
like, installing Rakali may interfere with exiting custom OpenCV builds so be sure to verify OpenCV versions
after installing Rakali. 


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

