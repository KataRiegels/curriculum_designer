from __future__ import annotations



from mdp import *
from samples import *
from features import *
import random as rand

def task_simplification(mdp : MDP, X = None, V = None, threshold = None):
    """Takes an MDP and returns a new MDP with a simplified feature"""
    # Copying parent MDP's features
    mdp_features = mdp.features.copy_features()

    
    attempt = 0
    max_attempt = 20
    while attempt < max_attempt:
        # Try/except due to possible generations where it tries to spawn e.g. key on pit.
        try:
            # Saves features in a copy so it can be tried again without the attempted modified features
            mdp_features_temp = mdp_features.copy_features()
            
            # Simplifies a random feature in the Feature dict
            mdp_features_temp.simplify_random_feature()
            
            # Create a new MDP with the simplified feature
            new_mdp = MDP(features = mdp_features_temp)
            new_mdp.task_type = "simp"
            
            return new_mdp
        except:
            if attempt > 5:
                print(f"simp attempt {attempt} - ", end = "")
            attempt += 1 
    if attempt>= max_attempt:    
        raise Exception()
            
def option_sub_goals(old_mdp : MDP, X: X, V = None, threshold = None):
    new_mdp = old_mdp.copy()
    (terminal_states, rewards) = find_high_value_states(old_mdp, X, V, threshold)
    new_mdp.specific_reward_values = rewards
    new_mdp.terminal_states = terminal_states
    new_mdp.task_type = "OSG"
    return new_mdp

def find_options():
    pass

def find_high_value_states(mdp : MDP, X: X, V = None, threshold = None):
    terminal_states = []
    rewards = {}
    reward = mdp.R
    for sample in X:
        old_state, action, new_state, reward = sample.get_attributes()
        # Get the Q value from V at state old_state
        value = V[old_state]
        max_value = max(V.values())
        # # value = mdp.value_function(old_state)
        if  value >= threshold:
            terminal_states.append(old_state)
            rewards[(old_state, action, new_state)] = value
    # print(f'terminal states: {len(terminal_states)}, reward: {len(rewards)}')
    return (set(terminal_states), rewards)







