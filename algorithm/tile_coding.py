import policy
import numpy as np

class TileCoding:
    def __init__(self, num_tilings, num_tiles_per_tiling, state_ranges):
        self.num_tilings = num_tilings
        self.num_tiles_per_tiling = num_tiles_per_tiling
        self.state_ranges = state_ranges
        self.tile_widths = [(r[1] - r[0]) / num_tiles_per_tiling for r in state_ranges]

    def encode(self, state):
        indices = []
        for i in range(self.num_tilings):
            tiling_offsets = [i * width / self.num_tilings for width in self.tile_widths]
            tile_indices = [(state - r[0] + offset) // width for state, r, offset, width in
                            zip(state, self.state_ranges, tiling_offsets, self.tile_widths)]
            indices.extend(tile_indices)
        return tuple(indices)