from __future__ import annotations

# from mdp import *

class X(list):
    
    def add_sample(self,old_state : State = None, action = None, new_state = None, reward = None ):
        self.append(Sample(old_state, action, new_state, reward))
    
    def count_same_states(self, other: X) -> int:
        other_states = other.get_states()
        common_states_count = sum(1 for sample in self if sample.old_state in other_states)
        return common_states_count 
    # def add_sample(self, x : Sample):
    #     self.append(x)
    
    
    def get_states(self) -> set[State]:
        states = set()
        for sample in self:
            if sample.old_state:
                states.add(sample.old_state)
        return states


class Sample:
    
    old_state = None
    action = None
    new_state = None
    reward = None   
    
    def __init__(self, old_state : State = None, action = None, new_state = None, reward = None ):
        self.old_state = old_state; self.action = action; self.new_state = new_state; self.reward = reward
        
    def get_attributes(self):
        return (self.old_state, self.action, self.new_state, self.reward)    
        
    pass








