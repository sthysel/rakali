# -*- encoding: utf-8 -*-
from glob import glob
from os.path import basename, splitext

from setuptools import find_packages, setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='rakali',
    license='MIT',
    version='0.0.7',
    description='OpenCV Helper Tools',
    long_description=long_description,
    long_description_content_type='text/markdown',
    entry_points={
        'console_scripts': [
            'rakali=rakali.cli.show:cli',
            'rakali-find-chessboards=rakali.cli.find_chessboards_live:cli',
            'rakali-pinhole-calibrate=rakali.cli.calibrate_pinhole:cli',
            'rakali-fisheye-calibrate=rakali.cli.calibrate_fisheye:cli',
            'rakali-find-ipcameras=rakali.cli.find_ip_cameras:cli',
            'rakali-undistort-pinhole=rakali.cli.undistort_pinhole:cli',
            'rakali-undistort-fisheye=rakali.cli.undistort_fisheye:cli',
            'rakali-view=rakali.cli.view_feed:cli',
        ],
    },
    install_requires=[
        'matplotlib',
        'click',
        'numpy',
        'scipy',
        'opencv-python',
        'imutils',
        'py-cpuinfo',
        'GPUtil',
    ],
    author='sthysel',
    author_email='sthysel@gmail.com',
    url='https://github.com/sthysel/rakali',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
    ],
    keywords=[],
    extras_require={},
    setup_requires=[],
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    package_data={
        'rakali/testimages': ['*.jpg'],
    },
)
