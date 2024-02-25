from __future__ import annotations
import random as rand


class Features(dict):
    
    def __init__(self, *features : Feature):
        for feature in features:
            if type(feature) == list:
                for feat in feature:
                    self[feat.get_feature_name()] = feat
                return
            self[feature.get_feature_name()] = feature
    
    
    def modify_feature(self, feature_name = None, new_feature : Feature = None):
        if feature_name == None:
            self[new_feature.get_feature_name()] = new_feature
        else:
            self[feature_name] = new_feature
    

    def get_random_feature(self):
        rand_feat = self[rand.choice(list(self.keys()))]
        return rand_feat
    
    def copy_features(self):
        copied_feats = Features(list(self.values()))
        # print("copying")
        return copied_feats

class Feature():

    def rng(self):
        raise Exception("No range for feature defined")
    
    def get_simplified(self) -> Feature:
        raise Exception("No get_simplified() function defined")
    
    def get_feature_name(self):
        raise Exception("No get_feature_name() function defined")
    


class TestFeat(Feature):
    def get_feature_name(self):
        return "test_feat"
    
    def get_simplified(self):
        return TestFeat()
    pass

class GridSize(Feature):
    
    def __init__(self, width = 10, height = 10, rng = (10, 10)):
        self.rng = rng
        self.height = height
        self.width = width
    
    def get_simplified(self):
        new_width = self.width
        new_height = self.width
        while(new_width == self.width and new_height == self.height):
            new_width = rand.randrange(0,self.width + 1) 
            new_height = rand.randrange(0,self.height + 1)
        return GridSize(width = new_width, height = new_height)
    
    def get_feature_name(self):
        return "grid_size"
    
    def rng(self):
        pass
    
    def __str__(self):
        return (f'({self.width} , {self.height})')
    
        
    def __lt__(self, other):
        return self.get_no_of_tiles() < other.get_no_of_tiles() 
    
    def __eq__(self, other):
        return self.get_no_of_tiles() == other.get_no_of_tiles() 
        
    def get_no_of_tiles(self):
        return self.height * self.width
    






