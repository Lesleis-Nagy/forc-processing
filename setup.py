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
        "scipy"
    ],
    entry_points="""
    [console_scripts]
    frc-to-forc=forc_processing.frc_to_forc.script:main
    forc-distributions=forc_processing.forc_distributions.script:main
    forc-average-loops=forc_processing.forc_average_loops.script:main
    """
)
