import numpy as np
from domains import Sensors

class TileCoder:
    def __init__(self, num_tiles, num_tilings, state_space_ranges):
        self.num_tiles = num_tiles
        self.num_tilings = num_tilings
        self.state_space_ranges = state_space_ranges
        self.tile_size = (np.array(state_space_ranges[:, 1], dtype=float) - np.array(state_space_ranges[:, 0], dtype=float)) / num_tiles

    def get_tile_index(self, tiling, sensor_value):
        """Returns the tile index for the given sensor index and value."""
        offset = tiling * self.tile_size[tiling]
        return int(np.floor(sensor_value / self.tile_size[tiling] + offset))


    def encode(self, state):
        """Takes a state and encodes it based on tile coding - Returns a Sensor object"""
        hole_sensor, beams_sensor, key_sensor, lock_sensor = state.hole_sensor, state.beams_sensor, state.key_sensor, state.lock_sensor

        for tiling in range(self.num_tilings):
            tiling_sensor_readings = []
            for sensor_reading in [hole_sensor, beams_sensor, key_sensor, lock_sensor]:
                sensor_reading = (sensor_reading[tiling])
                tiling_sensor_readings.append(self.get_tile_index(tiling, sensor_reading))
                #print(f"SENSOR READING {sensor_reading}")
                #print(self.get_tile_index(tiling, sensor_reading))
            encoded_sensors = Sensors(state.key_found, [tiling_sensor_readings[0]], [tiling_sensor_readings[1]], [tiling_sensor_readings[2]], [tiling_sensor_readings[3]])
            #print(f"ENCODED STATE: {encoded_sensors}")

        return encoded_sensors
