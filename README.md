# Rakali (Version 0.0.1)

Rakali is a imaging library and tool-set. It makes use of many other imaging libraries and frameworks and is
also intended to be used as a pedagogical resource for those.

![Rakali by Ravenari](docs/pics/rakali.jpg)
[1]

[1](By Ravenari)

## Install

Rakali is dependent on OpenCV, but because many people use their own builds of OpenCV to enable CUDA it is not
listed as a dependency in the setup.py. Listing `opencv-python`, which is the OpenCV most people use as it is
available on pypi, would clobber any locally built and installed OpenCV. So be sure to install OpenCV's python
bindings using either `$ pip install opencv-python` or your locally built OpenCV with CUDA or other ML
extensions after installing rakali.


