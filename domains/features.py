from __future__ import annotations
from mdp import *
import random as rand
import copy
import math

class Features(dict):
    """ A dictionary of Feature with helpful functions """
    
    def __init__(self, *features : Feature, run_with_print = False, mdp : MDP = None):
        self.run_with_print = run_with_print
        for feature in features:
            if type(feature) == list: # In case Features is initialized with a list instead of several args
                for feat in feature:
                    self[feat.get_feature_name()] = feat
                return
            self[feature.get_feature_name()] = feature
        
    """
    
    def run_dependencies(self):
        # Run through features to handle dependencies - e.g. hole with grid width
        for feature in self.values():
            feature.run_dependencies(self)
    """        
    
    def get_feature(self, feature : Feature):
        return self[feature.get_feature_name()]
    
    def modify_feature(self, feature_name : str = None, new_feature : Feature = None):
        """ Changes one given feature, new_feature, but keeps the rest"""
        if feature_name == None:
            self[new_feature.get_feature_name()] = new_feature
        else:
            self[feature_name] = new_feature
        if self.run_with_print: print(f'Feature modified: {new_feature.get_feature_name()}')
                # Run through features to handle dependencies - e.g. hole with grid width
        # for feature in self.values():
        #     feature.run_dependencies(self)
    
    def get_random_feature(self)    -> Feature:
        """ Get a random feature from the dictionary """
        rand_feat = self[rand.choice(list(self.keys()))]
        return rand_feat
    
    def simplify_random_feature(self):
        """ Takes a random Feature from the dictionary and simplifies it, if possible. Otherwise, picks another """
        possible_features = self.copy_features()
        while True:
            random_feature = self[rand.choice(list(possible_features.keys()))]
            # random_feature = self.get_random_feature()
            if random_feature.can_be_simplified():  
                break
            else: possible_features.pop(random_feature.get_feature_name())
        
        simplified_feat = random_feature.get_simplified()
        self.modify_feature(new_feature = simplified_feat)
        return 
    
    def copy_features(self) -> Features:
        """ Returns a copy of itself """
        copied_feats = Features(list(self.values()), run_with_print=self.run_with_print)
        return copied_feats

    def copy(self):
        return copy.deepcopy(self)

""" A sort of interface to ensure all Feature contain necessary functions"""
class Feature():
    feature_name = "No feature name"
    def rng(self):
        raise Exception("No range for feature defined")
    
    def get_simplified(self) -> Feature:
        """ Returns a simplified version of itself - Uses feature specific knowledge to determine what "simplify" means """
        raise Exception("No get_simplified() function defined")
    
    # def get_feature_name(self):
    #     """ All Feature types have an assigned string name - this gets said string """
    #     raise Exception("No get_feature_name() function defined")
    def get_feature_name(self):
        return self.feature_name
        """ All Feature types have an assigned string name - this gets said string """
        raise Exception("No get_feature_name() function defined")
    
    def can_be_simplified(self) -> bool:
        raise Exception("No can_be_simplified() function defined")
    
    """
    def run_dependencies(self, feature_dictionary : Features):
        # Changes variables that depend on other features - E.g. the hole depends on grid size
        return    
    """
    

class Hole(Feature):
    feature_name = "hole"
    def __init__(self, exists = False, width = 4, height = 1):
        self.exists = exists; self.width = width; self.height = height
        self.dependencies = [GridSize()]  
        self.hole_coordinates = []  
    
    def get_simplified(self) -> Feature:
        randint = rand.randint(1,self.width - 1)
        if randint == 0:
            self.exists = False
            return self
        else: 
            self.width = randint
        # self.update_hole()
            
            # self.set_hole_position()
        return self
    
    
    
    def can_be_simplified(self) -> bool:
        # return False
        return self.exists == True or self.width > 1
    
        """
    def run_dependencies(self, features : Features = None):
        Runs through dependencies - position, width and existance all depend on grid size 
        return
        for feature in self.dependencies:
            if type(feature) == GridSize:
                # grid_feature = feature_dictionary[GridSize().get_feature_name()]
                # If grid width is less than 3, we can't fit a hole there
                # hole made smaller than initially given if it can't fit in the grid
                # set the position such that it is in the middle of the grid
                
                mdp.grid.hole.calculate_coordinates(mdp.grid)

        """
    
    # A magic methods to be able to make use of the concept of Rng(F_i)
    def __lt__(self, other : Hole):
        if other.exists and not self.exists: return True
        if other.width > self.width: return True
        return False
    
    def __eq__(self, other: Hole):
        if (self.exists == other.exists): 
            if (self.exists):
                return self.width == other.width
            else:
                return True
        return False            
    

        
class GridSize(Feature):
    """ The grid size feature """
    
    def __init__(self, width = 10, height = 10, rng = (10, 10)):
        self.height = height
        self.width = width
        self.feature_name = "grid_size"
    
    def get_simplified(self):
        new_width = self.width
        new_height = self.height
        while(new_width == self.width and new_height == self.height):
            new_width = rand.randrange(max(3,self.width-2),self.width + 1) 
            new_height = rand.randrange(max(3,self.width-2),self.height + 1)
        print(f'Grid was simplified to size: {new_width}, {new_height}')
        return GridSize(width = new_width, height = new_height)
    
    def can_be_simplified(self):
        return self.width > 3 or self.height > 3
            
    
    def get_feature_name(self):
        """ Feature name for Features dictionary"""
        return "grid_size"
    
    def get_no_of_tiles(self):
        """ Helper method - To determine grid tile size """
        return self.height * self.width
    
    # string representation
    def __str__(self):
        return (f'({self.width} , {self.height})')
        
    # A magic methods to be able to make use of the concept of Rng(F_i)
    def __lt__(self, other):
        return self.get_no_of_tiles() < other.get_no_of_tiles() 
    
    def __eq__(self, other):
        return self.get_no_of_tiles() == other.get_no_of_tiles() 
        
    






