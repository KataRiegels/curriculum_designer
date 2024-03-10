from mdp import *

class X(list):
    
    def add_sample(self,old_state : State = None, action = None, new_state = None, reward = None ):
        self.append(Sample(old_state, action, new_state, reward))
    
    def add_sample(self, x):
        self.append(x)
    pass


class Sample:
    
    old_state = None
    action = None
    new_state = None
    reward = None
    
    def __init__(self, old_state : State = None, action = None, new_state = None, reward = None ):
        self.old_state = old_state; self.action = action; self.new_state = new_state; self.reward = reward
        
        
        
    pass








