import numpy as np

class CMAC:
    def __init__(self, num_tilings, tile_width, num_tiles):
        self.num_tilings = num_tilings
        self.tile_width = tile_width
        self.num_tiles = num_tiles
        self.weights = np.zeros(num_tilings * num_tiles)

    def get_tiles(self, state):
        tiles = []
        for i in range(self.num_tilings):
            offset = i * self.tile_width / self.num_tilings
            tile_indices = (state.to_np_save() + offset) // self.tile_width
            tiles.append(tile_indices)
        return tiles

    def get_value(self, state):
        tiles = self.get_tiles(state)
        value = 0
        for tile in tiles:
            value += self.weights[tile]
        return value

    def update_weights(self, state, target, learning_rate):
        tiles = self.get_tiles(state)
        for tile in tiles:
            self.weights[tile] += learning_rate * (target - self.get_value(state))
