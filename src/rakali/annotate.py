"""
This module provides some common helper functions to write on top of a image
"""

import cv2 as cv
from . import colors
import cpuinfo
import GPUtil

DEFAULT_POSITION = (10, 30)
FONT = cv.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.75
THICKNESS = 2
COLOR = colors.get('BLACK')


def GPU_label():
    """GPU label"""
    GPUs = GPUtil.getGPUs()
    labels = []
    for i, GPU in enumerate(GPUs):
        labels.append(f'GPU{i}: {GPU.name}')
        labels.append(f'Load: {GPU.load:.2f}')
        labels.append(f'Temp: {GPU.temperature}')

    return ', '.join(labels)


def CPU_label():
    """CPU label"""
    cpui = cpuinfo.get_cpu_info()
    cpu_label = f'CPU: {cpui["brand"]}, {cpui["hz_actual"]}, {cpui["arch"]}'
    return cpu_label


def add_frame_labels(
    frame,
    position=DEFAULT_POSITION,
    line_space=5,
    font=FONT,
    font_scale=FONT_SCALE,
    thickness=THICKNESS,
    color=colors.get('BHP'),
    labels=[],
):
    """
    Write each label on the image beginning at position being top left
    """

    text_size, _ = cv.getTextSize('sample text', font, font_scale, thickness)
    line_height = text_size[1] + line_space
    line_type = cv.LINE_AA

    x, y0 = position
    for i, line in enumerate(labels):
        y = y0 + i * line_height
        cv.putText(
            img=frame,
            text=line,
            org=(x, y),
            fontFace=font,
            fontScale=font_scale,
            color=color,
            thickness=thickness,
            lineType=line_type,
        )

    return frame
