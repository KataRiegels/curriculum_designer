from __future__ import annotations
import math
from collections import ChainMap

class Cell():
    
    x = None
    y = None
    value = None
    
    def __init__(self, x, y, value = None):
        self.x = x
        self.y = y    
        self._value = value
        
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if self._value is not None and new_value is not None:
            raise ValueError(f"Cannot change cell with value of {self._value} to {new_value} ")
        self._value = new_value
    
    pass

class Grid():
    
    
    
    size = None
    hole = []
    beams = []
    key = []
    lock = None
    
    def __init__(self, size = (10,10)):
        self.size = size
        self.cells = [[Cell(x, y) for y in range(self.size[0])] for x in range(self.size[1])]


   
    def get_cell(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[x][y]
        else:
            return None
            raise IndexError("Coordinates out of bounds")
    
    def assign_cell(self, cell = (None,None), cell_type = None):
        
        cell = self.get_cell(cell[0], cell[1])
        if cell:
            cell.value = cell_type
    
    def check_coordinate(self, coordinate):
        
        pass

    def build_grid(self):
        
        pass

    def add_object(self, object = None):
        object.create(self)
        for coordinate in object.coordinates:
            self.assign_cell(cell = (coordinate[0], coordinate[1]), cell_type = object.value)
 
    @property
    def width(self):
        return self.size[0]
    @property
    def height(self):
        return self.size[1]
    
    pass


class HoleObj():
    
    grid_size = None
    value = "hole"
    
    def __init__(self, width = 6, height = 1, exists = True):
        self.exists = exists
        self.height = height; self.width = width
        self.start = None
        self.even = width % 2 == 0
        self.coordinates = []
        self.start_x = None; self.start_y = None
        self.end_x = None;   self.end_y = None
    
    def calculate_coordinates(self, grid : Grid = None):
        # Finding the middle coordinate for the hole
        # x = math.ceil(grid.width/2)
        y = math.ceil(grid.size[1]/2)
        x = 2
        self.mid = [x,y]
        
        # For lower coordinates from middle coordinate
        # self.start_x = x - math.floor(self.width/2)
        self.start_y = y - math.floor(self.height/2)
        self.start_x = x
        self.start_y = y - math.floor(self.height/2)
        
        # for upper coordinates from middle coordinates
        self.end_x = x + self.width
        # self.end_x = x + math.floor(self.width/2)
        self.end_y = y + math.floor(self.height/2)
        
        # remove 1 coordinate step if the hole is even sized 
        # if self.is_width_even():  self.end_x -= 1
        if self.is_height_even(): self.end_y -= 1
        
        # calculate all the coordinates
        x_values = range(self.start_x, self.end_x + 1)  
        y_values = range(self.start_y, self.end_y + 1)  
        
        for x in x_values:
            for y in y_values:
                self.coordinates.append([x, y])
    
    def create(self, grid : Grid = None):
        if self.exists:
            self.calculate_coordinates(grid)
        
        self.beams = BeamsObj(self)
        grid.add_object(self.beams)
        # grid.beams = self.beams
        grid.hole = self
        
        pass
    
    def calculate_coordinates_2(self, grid : Grid = None):
        
        # Finding the middle coordinate for the hole
        x = math.ceil(grid.width/2)
        y = math.ceil(grid.height/2)
        self.mid = [x,y]
        
        # For lower coordinates from middle coordinate
        self.start_x = x - math.floor(self.width/2)
        self.start_y = y - math.floor(self.height/2)
        
        # for upper coordinates from middle coordinates
        self.end_x = x + math.floor(self.width/2)
        self.end_y = y + math.floor(self.height/2)
        
        # remove 1 coordinate step if the hole is even sized 
        if self.is_width_even():  self.end_x -= 1
        if self.is_height_even(): self.end_y -= 1
        
        # calculate all the coordinates
        x_values = range(self.start_x, self.end_x + 1)  
        y_values = range(self.start_y, self.end_y + 1)  
        
        for x in x_values:
            for y in y_values:
                self.coordinates.append([x, y])
        
        
        pass

    def is_width_even(self):
        self.even = self.width % 2 == 0
        return self.even

    def is_height_even(self):
        even = self.height % 2 == 0
        return even


class HoleObj2():
    
    grid_size = None
    
    def __init__(self, width = 6, height = 1, exists = True):
        self.exists = exists
        self.height = height; self.width = width
        self.mid = None
        self.even = width % 2 == 0
        self.coordinates = []
        self.start_x = None; self.start_y = None
        self.end_x = None;   self.end_y = None
    
    
    
    def calculate_coordinates_2(self, grid : Grid = None):
        
        # Finding the middle coordinate for the hole
        x = math.ceil(grid.width/2)
        y = math.ceil(grid.height/2)
        self.mid = [x,y]
        
        # For lower coordinates from middle coordinate
        self.start_x = x - math.floor(self.width/2)
        self.start_y = y - math.floor(self.height/2)
        
        # for upper coordinates from middle coordinates
        self.end_x = x + math.floor(self.width/2)
        self.end_y = y + math.floor(self.height/2)
        
        # remove 1 coordinate step if the hole is even sized 
        if self.is_width_even():  self.end_x -= 1
        if self.is_height_even(): self.end_y -= 1
        
        # calculate all the coordinates
        x_values = range(self.start_x, self.end_x + 1)  
        y_values = range(self.start_y, self.end_y + 1)  
        
        for x in x_values:
            for y in y_values:
                self.coordinates.append([x, y])
        
        
        pass

    def is_width_even(self):
        self.even = self.width % 2 == 0
        return self.even

    def is_height_even(self):
        even = self.height % 2 == 0
        return even


class BeamsObj():
    
    value = "beam"
    
    def __init__(self, hole = None):
        self.hole = hole
        self.coordinates = []
        self.locate_beams(hole = self.hole)

    def locate_beams(self, hole : HoleObj):
        if hole.exists:
            self.coordinates = [
                [hole.start_x - 1, hole.start_y - 1],
                [hole.end_x + 1,   hole.start_y - 1],
                [hole.start_x - 1, hole.end_y + 1],
                [hole.end_x + 1,   hole.end_y + 1]
            ]   
       
    def create(self, grid : Grid):
        grid.beams = self
        
    pass

class KeyObj():
    
    value = "key"
    
    def __init__(self, grid : Grid = None, exists = True):
        self.coordinate = [0,0]
        self.coordinates = [self.coordinate]
        self.exists = exists
    
    def create(self, grid : Grid = None):
        self.grid = grid
        grid.key = self
        self.calculate_coordinates(grid)
    
    def calculate_coordinates(self, grid : Grid = None):
        if grid.height > 1:
            self.coordinate[1] = grid.height - 2
        else:
            self.coordinate[1] = 0
        if grid.width > 1:
            self.coordinate[0] = grid.width - 2
        else:
            self.coordinate[0] = 0
        
        pass
    pass

class LockObj():
    
    value = "lock"
    
    def __init__(self, grid : Grid = None, exists = True):
        self.coordinate = [0,0]
        self.coordinates = [self.coordinate]
        self.exists = exists
    
    def create(self, grid : Grid = None):
        self.grid = grid
        grid.lock = self
        self.calculate_coordinates(grid)
    
    def calculate_coordinates(self, grid : Grid = None):
        if grid.height > 1:
            self.coordinate[1] =  1
        else:
            self.coordinate[1] = 0
        if grid.width > 1:
            self.coordinate[0] = 1
        else:
            self.coordinate[0] = 0
        
        pass
    pass
    pass





