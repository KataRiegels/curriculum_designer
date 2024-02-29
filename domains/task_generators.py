from __future__ import annotations



from mdp import *
from features import *
import random as rand

def task_simplification(mdp : MDP):
    """Takes an MDP and returns a new MDP with a simplified feature"""
    # Copying parent MDP's features
    mdp_features = mdp.features.copy_features()
    
    
    
    while True:
        # Try/except due to possible generations where it tries to spawn e.g. key on pit.
        try:
            # Saves features in a copy so it can be tried again without the attempted modified features
            mdp_features_temp = mdp_features.copy_features()
            
            # Simplifies a random feature in the Feature dict
            mdp_features_temp.simplify_random_feature()
            
            # Create a new MDP with the simplified feature
            new_mdp = MDP(features = mdp_features_temp)
            return new_mdp
        except:
            print("Simplification faled. Trying again") 







