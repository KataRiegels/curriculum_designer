import numpy as np
from domains import Sensors

class TileCoder:
    def __init__(self, num_tiles, num_tilings, state_space_ranges):
        self.num_tiles = num_tiles
        self.num_tilings = num_tilings
        self.state_space_ranges = state_space_ranges
        self.tile_size = (np.array(state_space_ranges[:, 1], dtype=float) - np.array(state_space_ranges[:, 0], dtype=float)) / num_tiles
        print(f'tile_size: {self.tile_size}')

    def get_tile_index(self, tiling, sensor_value):
        """Returns the tile index for the given sensor index and value."""
        offset = tiling * self.tile_size[tiling]
        # print(f'sensor values: {sensor_value}')
        return int(np.floor(sensor_value / self.tile_size[tiling] + offset))


    def encode(self, state : Sensors):
        """Takes a state and encodes it based on tile coding - Returns a Sensor object"""
        hole_sensor, beams_sensor, key_sensor, lock_sensor = state.hole_sensor, state.beams_sensor, state.key_sensor, state.lock_sensor

        for tiling in range(self.num_tilings):
            tiling_sensor_readings = []
            for sensor_reading in [hole_sensor, beams_sensor, key_sensor, lock_sensor]:
                sensor_reading = (sensor_reading[tiling])
                tiling_sensor_readings.append(self.get_tile_index(tiling, sensor_reading))
                #print(f"SENSOR READING {sensor_reading}")
                #print(self.get_tile_index(tiling, sensor_reading))
            encoded_sensors = Sensors(key_found = state.key_found, hole_sensor = [tiling_sensor_readings[0]], beams_sensor=[tiling_sensor_readings[1]], key_sensor=[tiling_sensor_readings[2]], lock_sensor=[tiling_sensor_readings[3]])
            #print(f"ENCODED STATE: {encoded_sensors}")

        return encoded_sensors
    
    
    def generate_feature_vector(self, sensor : Sensors, tile_width=1, num_tiles=3):
        feature_vector = []
        sensor_readings = []
        [sensor_readings.extend(l) for l in (sensor.hole_sensor , sensor.beams_sensor , sensor.key_sensor , sensor.lock_sensor)]
        sensor_readings.append(sensor.key_found )
        # sensor_readings = sensor.key_found + sensor.hole_sensor + sensor.beams_sensor + sensor.key_sensor + sensor.lock_sensor
        for sensor_value in sensor_readings:
            # For simplicity, let's assume each sensor value corresponds to the center of a tile
            # Create tiles around the sensor value
            tiles = np.linspace(sensor_value - tile_width, sensor_value + tile_width, num=num_tiles)
            # Convert sensor value to binary feature variables based on tile coding
            feature_values = [1 if sensor_value >= tile_start and sensor_value <= tile_end else 0 for tile_start, tile_end in zip(tiles[:-1], tiles[1:])]
            # Append feature values to feature vector
            feature_vector.extend(feature_values)
        return feature_vector