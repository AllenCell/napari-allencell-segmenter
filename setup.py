#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup, find_packages


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding="utf-8").read()


# Add your dependencies in requirements.txt
# Note: you can add test-specific requirements in tox.ini
requirements = [
    "napari>=0.4.9",
    "napari-plugin-engine>=0.1.4",
    "numpy",
    "aicssegmentation ~= 0.4.1",
    "magicgui >= 0.2.9",
    "aicsimageio ~= 4.0.5",
    "opencv-python-headless>=4.5.1",
]

test_requirements = [
    "black>=19.10b0",
    "codecov>=2.0.22",
    "docutils>=0.10,<0.16",
    "flake8>=3.7.7",
    "psutil>=5.7.0",
    "pytest>=4.3.0",
    "pytest-cov==2.6.1",
    "pytest-raises>=0.10",
    "pytest-qt>=3.3.0",
    "quilt3>=3.1.12",
]

dev_requirements = [
    "black>=19.10b0",
    "bumpversion>=0.5.3",
    "coverage>=5.0a4",
    "docutils>=0.10,<0.16",
    "flake8>=3.7.7",
    "gitchangelog>=3.0.4",
    "ipython>=7.5.0",
    "m2r>=0.2.1",
    "pytest>=4.3.0",
    "pytest-cov==2.6.1",
    "pytest-raises>=0.10",
    "pytest-runner>=4.4",
    "pytest-qt>=3.3.0",
    "quilt3>=3.1.12",
    "Sphinx>=2.0.0b1,<3",
    "sphinx_rtd_theme>=0.1.2",
    "tox>=3.5.2",
    "twine>=1.13.0",
    "wheel>=0.33.1",
]

setup_requirements = [
    "pytest-runner",
]

extra_requirements = {
    "test": test_requirements,
    "dev": dev_requirements,
    "setup": setup_requirements,
    "all": [
        *requirements,
        *test_requirements,
        *setup_requirements,
        *dev_requirements,
    ],
}


# https://github.com/pypa/setuptools_scm
use_scm = {"write_to": "napari_allencell_segmenter/_version.py"}

setup(
    name="napari-allencell-segmenter",
    author="Allen Institute for Cell Science",
    license="BSD-3",
    url="https://github.com/AllenCell/napari-allencell-segmenter",
    description="A plugin that enables 3D image segmentation provided by Allen Institute for Cell Science",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=requirements,
    use_scm_version=use_scm,
    setup_requires=setup_requirements,
    test_suite="napari_allencell_segmenter/_tests",
    tests_require=test_requirements,
    extras_require=extra_requirements,
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Framework :: napari",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: BSD License",
    ],
    entry_points={
        "napari.plugin": [
            "napari-allencell-segmenter = napari_allencell_segmenter",
        ],
    },
    # Do not edit this string manually, always use bumpversion
    # Details in CONTRIBUTING.rst
    version="1.1.3",
    zip_safe=False,
)
