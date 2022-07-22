import numpy as np
import pandas as pd


class ForcMinorLoop:
    r"""
    Class to encapsulate a FORC minor loop.
    """
    def __init__(self):
        self.observations = []
        self.Br = None

    def add_observation(self, B: float, M: float):
        if not self.observations:
            self.Br = B
        self.observations.append((B, M))

    def is_empty(self):
        if not self.observations:
            return True
        return False

    def reverse(self):
        self.observations.reverse()

    def __str__(self):
        output = ""

        output += f"========== B: {self.Br:20.15} ==========\n"
        for B, M in self.observations:
            output += f"{B:20.15e}\t{M:20.15e}\n"

        return output


class ForcMinorLoops:

    def __init__(self):
        self.minor_loops = []

        # The number of observations in the biggest loop.
        self.max_loop_size = 0

        # The loop with the most observations.
        self.max_loop = None

    def is_empty(self):
        if not self.minor_loops:
            return True
        return False

    def append(self, minor_loop):
        self.minor_loops.append(minor_loop)

        size = len(minor_loop.observations)
        if size > self.max_loop_size:
            self.max_loop_size = size
            self.max_loop = minor_loop

    def loops_to_slab(self):
        forc_slab = np.zeros((self.max_loop_size, self.max_loop_size))
        for i, minor_loop in enumerate(self.minor_loops):
            for j, observation in enumerate(reversed(minor_loop.observations)):
                jj = self.max_loop_size - 1 - j
                forc_slab[i, jj] = observation[1]

        return forc_slab

    def all_fields(self):
        return [p[0] for p in self.max_loop.observations]

    def reverse(self):
        self.minor_loops.reverse()

    def __str__(self):
        output = f"Maximum loop size {self.max_loop_size}\n"

        for minor_loop in self.minor_loops:
            output += f"{minor_loop}\n"

        return output


def read_frc(file_name: str):
    r"""
    Read an FORC file in '*.frc' format.
    :param file_name: the FORC file name.
    :output: an array of blocks, each block is a FORC.
    """
    with open(file_name, "r") as fin:
        forc_minor_loops = ForcMinorLoops()
        forc_minor_loop = ForcMinorLoop()
        for line in fin:
            line = line.strip()
            if line == "":
                forc_minor_loops.append(forc_minor_loop)
                forc_minor_loop = ForcMinorLoop()
            elif line == "END":
                break
            else:
                B, M = [float(v) for v in line.split(",")]
                forc_minor_loop.add_observation(B, M)

        return forc_minor_loops

def calculate_dot_product(row):
    return row[1]*row[4] + row[2]*row[5] + row[3]*row[6]

def read_loop(file_name: str):
    r"""
    Read a FORC file in '*.loop' format.
    :param file_name: the FORC file name.
    :output: an array of blocks, each block is a FORC.
    """
    df = pd.read_csv(file_name)
    columns = {column_name: column_name.strip() for column_name in df.columns.values}
    df.rename(columns=columns, inplace=True)
    grouped = df.groupby("Br")
    br_fields = grouped.groups.keys()

    forc_minor_loops = ForcMinorLoops()
    for group_key, gdf in grouped:
        gdf['M.H'] = gdf.apply(calculate_dot_product, axis=1)
        forc_minor_loop = ForcMinorLoop()
        for index, row in gdf.iterrows():
            forc_minor_loop.add_observation(row["B (Tesla)"], row["M.H"])
        forc_minor_loops.append(forc_minor_loop)

    return forc_minor_loops
