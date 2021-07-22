import click
import cv2 as cv
from rakali import transforms
from rakali.annotate import add_frame_labels, colors
from rakali.camera.fisheye import CalibratedFisheyeCamera


@click.command(context_settings=dict(max_content_width=120))
@click.version_option()
@click.argument(
    "image-path",
    type=click.Path(exists=True),
)
@click.option(
    "--calibration-file",
    help="Camera calibration data",
    default="fisheye_calibration.json",
    type=click.Path(exists=True),
    show_default=True,
    required=True,
)
@click.option(
    "-b",
    "--balance",
    help="Balance value 0.0 ~30% pixel loss, 1.0 no loss",
    default=1.0,
    show_default=True,
)
@click.option(
    "-s",
    "--scale",
    help="Scale image",
    default=0.5,
    show_default=True,
)
def cli(image_path, calibration_file, balance, scale):
    """
    Rectify a image taken with a fish-eye lens camera using calibration parameters
    """
    window_name = "Undistorted fisheye"
    cv.namedWindow(window_name)

    def update():
        rectified = camera.correct(img)
        labels = [
            f"Reprojected fisheye frame",
            f"undistort cost: {camera.correct.cost:6.3f}s",
            f"balance: {camera.balance}",
            f"cid: {camera.cid} calibrated on {camera.calibration_time_formatted}",
            # f'dim2 {dim2}',
            # f'dim3 {dim3}',
        ]
        labeled_frame = add_frame_labels(
            frame=rectified,
            labels=labels,
            color=colors.get("BHP"),
        )
        cv.imshow(window_name, labeled_frame)
        cv.imshow("Raw image", img)

    def on_balance(balance):
        camera.set_balance(balance=balance / 100, frame=img)
        update()

    def on_width(width):
        camera.set_size(w=width, h=source_height, frame=img)
        update()

    cv.createTrackbar("Balance", window_name, int(balance * 100), 100, on_balance)
    cv.createTrackbar("Width", window_name, 100, 4000, on_width)

    camera = CalibratedFisheyeCamera(
        calibration_file=calibration_file,
        balance=balance,
        dim2=None,
        dim3=None,  # remember we have these
    )

    img = transforms.scale(cv.imread(image_path), scale)
    source_height, source_width = img.shape[:2]
    camera.set_map(first_frame=img)

    on_balance(balance * 100)
    while True:
        if cv.waitKey(1) & 0xFF == ord("q"):
            break
