import unittest

import numpy as np

import matplotlib.pyplot as plt
from matplotlib.cm import RdBu_r

from forc_processing.frc_to_forc.script import shiftedColorMap
from forc_processing.frc_to_forc.script import plot_forc_distribution
from forc_processing.frc_to_forc.script import forc_distribution

from forc_processing.file_io.forc_file_reader import read_frc

class TestReadFRC(unittest.TestCase):

    def test_read_frc(self):
        forcs = read_frc("../test_data/00000_20C_1p00pc_045nm.frc")

        print(forcs.loops_to_slab())
        print(forcs.all_fields())

    def test_make_pdf(self):
        forcs = read_frc("../test_data/00000_20C_1p00pc_045nm.frc")

        forc_slab = forcs.loops_to_slab()
        field = forcs.all_fields()
        scalar = 1000.0
        scaled_field = [scalar*h for h in field]

        # Scaling factor
        sf = 3

        Bb, Ba = np.meshgrid(scaled_field, scaled_field[::-1])
        rho = forc_distribution(forc_slab, Bb, Ba, sf)

        xlim = [0.0, 200.0]
        ylim = [-200.0, 200.0]
        shiftedCMap = shiftedColorMap(RdBu_r, midpoint=(0.5))
        major = 20.0
        minor = 20.0
        annotate = ["this is an annotation"]
        contour_start = 0.1
        contour_end = 1.3
        contour_step = 0.3

        fig, ax = plot_forc_distribution(
            Bb, Ba, rho,
            xlim, ylim,
            major, minor,
            shiftedCMap, annotate,
            contour_start,
            contour_end,
            contour_step)
        fig.savefig("00000_20C_1p00pc_045nm.pdf")

        plt.close()
