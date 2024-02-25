from __future__ import annotations
import random as rand


class Features(dict):
    """ A dictionary of Feature with helpful functions """
    
    def __init__(self, *features : Feature, run_with_print = False):
        self.run_with_print = run_with_print
        for feature in features:
            if type(feature) == list: # In case Features is initialized with a list instead of several args
                for feat in feature:
                    self[feat.get_feature_name()] = feat
                return
            self[feature.get_feature_name()] = feature
    
    def modify_feature(self, feature_name : str = None, new_feature : Feature = None):
        """ Changes one given feature, new_feature, but keeps the rest"""
        if feature_name == None:
            self[new_feature.get_feature_name()] = new_feature
        else:
            self[feature_name] = new_feature
        if self.run_with_print: print(f'Feature modified: {new_feature.get_feature_name()}')
    
    def get_random_feature(self)    -> Feature:
        """ Get a random feature from the dictionary """
        rand_feat = self[rand.choice(list(self.keys()))]
        return rand_feat
    
    def copy_features(self) -> Feature:
        """ Returns a copy of itself """
        copied_feats = Features(list(self.values()), run_with_print=self.run_with_print)
        return copied_feats

""" A sort of interface to ensure all Feature contain necessary functions"""
class Feature():

    def rng(self):
        raise Exception("No range for feature defined")
    
    def get_simplified(self) -> Feature:
        """ Returns a simplified version of itself - Uses feature specific knowledge to determine what "simplify" means """
        raise Exception("No get_simplified() function defined")
    
    def get_feature_name(self):
        """ All Feature types have an assigned string name - this gets said string """
        raise Exception("No get_feature_name() function defined")
    


class TestFeat(Feature):
    def get_feature_name(self):
        return "test_feat"
    
    def get_simplified(self):
        return TestFeat()
    pass

""" The grid size feature """
class GridSize(Feature):
    
    def __init__(self, width = 10, height = 10, rng = (10, 10)):
        self.rng = rng
        self.height = height
        self.width = width
    
    def get_simplified(self):
        new_width = self.width
        new_height = self.height
        while(new_width == self.width and new_height == self.height):
            new_width = rand.randrange(1,self.width + 1) 
            new_height = rand.randrange(1,self.height + 1)
        return GridSize(width = new_width, height = new_height)
    
    
    
    def get_feature_name(self):
        """ Feature name for Features dictionary"""
        return "grid_size"
    
    def rng(self):
        pass
    
    
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
        
    






