import numpy as np

class TileCoder:
    def __init__(self, num_tiles, num_tilings, state_space_ranges):
        self.num_tiles = num_tiles
        self.num_tilings = num_tilings
        self.state_space_ranges = state_space_ranges
        self.tile_size = (np.array(state_space_ranges[:, 1], dtype=float) - np.array(state_space_ranges[:, 0], dtype=float)) / num_tiles

    def encode(self, state):
        hole_sensor, beams_sensor, key_sensor, lock_sensor = state.hole_sensor, state.beams_sensor, state.key_sensor, state.lock_sensor
        tilings_indices = []
        for tiling in range(self.num_tilings):
            tiling_indices = []
            for i, (sensor_reading, (sensor_min, sensor_max)) in enumerate(
                    zip([hole_sensor, beams_sensor, key_sensor, lock_sensor], self.state_space_ranges)):
                sensor_reading = float(sensor_reading[tiling])
                sensor_index = min(int((sensor_reading - sensor_min) / self.tile_size[i]), self.num_tiles - 1)
                tiling_indices.append(sensor_index)
            tilings_indices.append(tiling_indices)
            return tilings_indices