from __future__ import annotations
import math
from collections import ChainMap

class Cell():
    """Class to represent each cell in a Grid"""
    x = None
    y = None
    value = None
    
    def __init__(self, x, y, value = None):
        self.x = x
        self.y = y    
        self._value = value
        
    @property
    def value(self):
        """ Allows to make sure value is only changed when allowed"""
        return self._value

    @value.setter
    def value(self, new_value):
        """Allows to make sure value is only changed when allowed"""
        if self._value is not None and new_value is not None:
            raise ValueError(f"Cannot change cell with value of {self._value} to {new_value} ")
        self._value = new_value
    
class Grid():
    """Grid representation"""
    
    size = None
    hole = []
    hole_cells = []
    beams = []
    beams_cells = []
    key = []
    key_cells = []
    lock = None
    lock_cells = []
    
    # Structure here to make it faster to look for certain cell types
    objects_dict = {
        "hole" : [],
        "beams" : [],
        "key" : [],
        "lock" : [],
    }
    
    def __init__(self, size = (10,10)):
        self.size = size
        
        # Initialize all Cells
        self.cells = [[Cell(x, y) for y in range(self.size[0])] for x in range(self.size[1])]


   
    def get_cell(self, x, y):
        """Returns a Cell instance corresponding to the coordinate"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[x][y]
        else:
            return None
            raise IndexError("Coordinates out of bounds")
    
    def assign_cell(self, cell = (None,None), cell_type = None):
        """Assign a cell type to a Cell"""
        cell = self.get_cell(cell[0], cell[1])
        if cell:
            cell.value = cell_type
            if cell.value != None:
                self.objects_dict[cell_type].append(cell)
            else:
                self.neutralize_cell(cell)
    
    def neutralize_cell(self, cell):
        """Removes an object from a cell - e.g. when removing a picked up"""
        if cell.value is not None:
            self.objects_dict[cell.value].remove(cell)
        cell.value = None
                
    def check_coordinate(self, coordinate):
        """Return the cell type at given coordinate"""
        return self.get_cell(coordinate[0], coordinate[1]).value

    def add_object(self, object = None):
        """Adds an objects, this its corresponding coordinates, to cells in the Grid"""
        object.create(self)
        for coordinate in object.coordinates:
            self.assign_cell(cell = (coordinate[0], coordinate[1]), cell_type = object.value)
 
    def distance_to_nearest(self, agent, sensor_type):
        """Determine the distance to the nearest cell with *sensor_type*"""
        # Manhatten?
        if sensor_type not in ["hole", "beams", "key", "lock"]:
            raise ValueError(f"Invalid sensor_type: {sensor_type}")

        agent_x, agent_y = agent
        min_distance = float('inf')

        for cell in self.objects_dict[sensor_type]:
            distance = math.sqrt((cell.x - agent_x)**2 + (cell.y - agent_y)**2)
            min_distance = min(min_distance, distance)


        return round(min_distance, 2)
 
    def is_hole_adjacent(self, coordinate):
        """Checks if there's a hole next to the coordinate"""
        x, y = coordinate
        adjacent_coordinates = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]

        for adj_x, adj_y in adjacent_coordinates:
            if 0 <= adj_x < self.width and 0 <= adj_y < self.height:
                if self.get_cell(adj_x, adj_y).value == "hole":
                    return True
        return False
 
    @property
    def width(self):
        return self.size[0]
    @property
    def height(self):
        return self.size[1]
    


class HoleObj():
    """Class to represent the pit"""
    grid_size = None
    value = "hole"
    
    def __init__(self, width = 6, height = 1, exists = True):
        self.exists = exists
        self.height = height; self.width = width
        self.coordinates = []
        self.start_x = None; self.start_y = None
        self.end_x = None;   self.end_y = None
    
    def calculate_coordinates(self, grid : Grid = None):
        """Sets the list of hole coordinates"""
        
        # Finding the middle coordinate for the hole
        # x = math.ceil(grid.width/2)
        y = math.ceil(grid.size[1]/2)
        x = 2
        self.mid = [x,y]
        
        self.start_x = x
        self.start_y = y - math.floor(self.height/2)
        
        # for upper coordinates from middle coordinates
        self.end_x = x + self.width
        self.end_y = y + math.floor(self.height/2)
        
        # remove 1 coordinate step if the hole is even sized 
        if self.is_height_even(): self.end_y -= 1
        
        # calculate all the coordinates
        x_values = range(self.start_x, self.end_x + 1)  
        y_values = range(self.start_y, self.end_y + 1)  
        
        for x in x_values:
            for y in y_values:
                self.coordinates.append([x, y])
    
    def create(self, grid : Grid = None):
        """Adds the pit and corresponding beams to the Grid"""
        if self.exists:
            self.calculate_coordinates(grid)
        
        self.beams = BeamsObj(self)
        grid.add_object(self.beams)
        grid.hole = self
        
        pass

    def is_width_even(self):
        self.even = self.width % 2 == 0
        return self.even

    def is_height_even(self):
        even = self.height % 2 == 0
        return even


class BeamsObj():
    """Class for representing pit beams on the Grid"""
    
    value = "beams"
    
    def __init__(self, hole = None):
        self.hole = hole
        self.coordinates = []
        self.locate_beams(hole = self.hole)

    def locate_beams(self, hole : HoleObj):
        """Sets coordinates based off of the given hole"""
        if hole.exists:
            self.coordinates = [
                [hole.start_x - 1, hole.start_y - 1],
                [hole.end_x + 1,   hole.start_y - 1],
                [hole.start_x - 1, hole.end_y + 1],
                [hole.end_x + 1,   hole.end_y + 1]
            ]   
       
    def create(self, grid : Grid):
        """Add beams to the grid"""
        grid.beams = self
        

class KeyObj():
    """Class for representing keys on the Grid"""
    
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
        """Set key coordinates"""
        if grid.height > 1:
            self.coordinate[1] = grid.height - 2
            #self.coordinate[1] = 1
        else:
            self.coordinate[1] = 0
        if grid.width > 1:
            self.coordinate[0] = grid.width - 2
            #self.coordinate[0] = 6
        else:
            self.coordinate[0] = 0
        
        pass
    pass

class LockObj():
    """Class for representing locks on the Grid"""
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
        """Set lock coordinates"""
        if grid.height > 1:
            self.coordinate[1] =  1
        else:
            self.coordinate[1] = 0
        if grid.width > 1:
            self.coordinate[0] = 1
        else:
            self.coordinate[0] = 0
        





