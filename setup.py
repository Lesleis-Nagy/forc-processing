#!/usr/scripts/env python

from setuptools import setup, find_packages

setup(
    name="forc-processing",
    version="1.0.0",
    packages=find_packages(
        where="lib",
        include="forc_processing/*",
    ),
    package_dir={"": "lib"},
    install_requires=[
        "typer",
        "rich",
        "numpy",
        "matplotlib",
        "pandas",
        "scipy",
        "PyQt6",
        "PyQt6-Charts",
        "pillow",
        "pyyaml",
        "pyqtgraph",
        "PyOpenGL"
    ],
    include_package_data=True,
    entry_points="""
    [console_scripts]
    forc-gui=forc_processing.gui.main:main
    forc-cli=forc_processing.cli.main:main
    """
)
