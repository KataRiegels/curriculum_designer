


from mdp import *
from features import *
import random as rand
F_vec = Features(GridSize(), TestFeat())

mdp = MDP(features = F_vec)

def task_simplification(mdp : MDP):
    mdp_features = mdp.features.copy_features()
    feat : Feature = mdp.features.get_random_feature()
    simplified_feat = feat.get_simplified()
    mdp_features.modify_feature(simplified_feat.get_feature_name(), simplified_feat)
    new_mdp = MDP(features = mdp_features)
    print(new_mdp)
    pass


task_simplification(mdp)






