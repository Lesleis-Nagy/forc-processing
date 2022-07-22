import typer

import numpy as np

import matplotlib.pyplot as plt
from matplotlib.cm import RdBu_r

from forc_processing.frc_to_forc.script import shiftedColorMap
from forc_processing.frc_to_forc.script import forc_distribution
from forc_processing.frc_to_forc.script import plot_forc_distribution

from forc_processing.file_io.forc_file_reader import read_loop

app = typer.Typer()

@app.command()
def single_forc(loop_file: str, output: str, sf: int = 3,
                xmin: float = 0.0, xmax: float = 200.0,
                ymin: float = -200.0, ymax: float = 200.0,
                major: float = 20.0, minor: float = 20.0,
                contour_start: float = 0.1,
                contour_step: float = 0.3,
                contour_end: float = 1.3,
                dpi=300):

    forcs = read_loop(loop_file)
    forcs.reverse()

    forc_slab = forcs.loops_to_slab()
    field = forcs.all_fields()
    scalar = 1000.0
    scaled_field = [scalar * h for h in field]

    Bb, Ba = np.meshgrid(scaled_field, scaled_field[::-1])
    rho = forc_distribution(forc_slab, Bb, Ba, sf)

    xlim = [xmin, xmax]
    ylim = [ymin, ymax]
    shiftedCMap = shiftedColorMap(RdBu_r, midpoint=(0.5))

    annotate = []

    fig, ax = plot_forc_distribution(
        Bb, Ba, rho,
        xlim, ylim,
        major, minor,
        shiftedCMap, annotate,
        contour_start,
        contour_end,
        contour_step)
    fig.savefig(output)


def main():
    app()
