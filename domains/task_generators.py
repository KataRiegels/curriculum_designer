from __future__ import annotations



from mdp import *
from features import *
import random as rand
# F_vec = Features(GridSize(), TestFeat(), run_with_print=True)

# mdp = MDP(features = F_vec, run_with_print=True)

def task_simplification(mdp : MDP):
    # Copying parent MDP's features
    mdp_features = mdp.features.copy_features()
    
    
    """
    # Determine random feature to simplify
    feat : Feature = mdp.features.get_random_feature()
    simplified_feat = feat.get_simplified()
    
    # create new MDP with modified version of parent MDP
    mdp_features.modify_feature(simplified_feat.get_feature_name(), simplified_feat)
    """
    mdp_features.simplify_random_feature()
    new_mdp = MDP(features = mdp_features)
    print(new_mdp)
    return new_mdp
    pass


# task_simplification(mdp)






