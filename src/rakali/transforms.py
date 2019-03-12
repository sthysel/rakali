import cv2 as cv


def scale(img, scale):
    """scale preserving aspect ratio"""
    return resize(img, x_scale=scale, y_scale=scale)


def resize(img, x_scale, y_scale, optimize=True):
    """resize image by scaling using provided factors"""
    interpolation = cv.INTER_LINEAR

    # pick an optimized scaler if asked to
    if optimize:
        if x_scale > 1 and y_scale > 1:
            interpolation = cv.INTER_CUBIC
        else:
            interpolation = cv.INTER_AREA

    return cv.resize(
        img,
        None,
        fx=x_scale,
        fy=y_scale,
        interpolation=interpolation,
    )
