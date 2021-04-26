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
    "napari>=0.4.7",
    "napari-plugin-engine>=0.1.4",
    "numpy",
    "aicssegmentation @ git+https://github.com/AllenCell/aics-segmentation.git@feature/workflow-engine#egg=aicssegmentation",
    "magicgui >= 0.2.9",
    "aicsimageio>=3.3.4,<4",
    "opencv-python-headless>=4.5.1",
]

test_requirements = [
    "black==19.10b0",
    "codecov>=2.0.22",
    "docutils>=0.10,<0.16",
    "flake8>=3.7.7",
    "napari[pyqt5]>=0.2.10",
    "psutil>=5.7.0",
    "pytest>=4.3.0",
    "pytest-cov==2.6.1",
    "pytest-raises>=0.10",
    "pytest-qt>=3.3.0",
    "quilt3>=3.1.12",
]

dev_requirements = [
    "black==19.10b0",
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
    "setuptools_scm",
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
use_scm = {"write_to": "napari_aicssegmentation/_version.py"}

setup(
    name="napari-aicssegmentation",
    author="Jamie Sherman",
    author_email="jamies@alleninstitute.org",
    license="BSD-3",
    url="https://github.com/heeler/napari-aicssegmentation",
    description="A plugin that enables image segmentation provided by AICS",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=requirements,
    use_scm_version=use_scm,
    setup_requires=setup_requirements,
    test_suite="napari_aicssegmentation/_tests",
    tests_require=test_requirements,
    extras_require=extra_requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Framework :: napari",
        "Topic :: Software Development :: Testing",
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
            "napari-aicssegmentation = napari_aicssegmentation",
        ],
    },
    # Do not edit this string manually, always use bumpversion
    # Details in CONTRIBUTING.rst
    version="0.0.0",
    zip_safe=False,
)
