from __future__ import annotations

# from agent import Agent
from grid_representation import *
from features import *
import random as rand

class State():
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y
        
    def position(self):
        return (self.x, self.y)
        
    def copy(self):
        return State(x = self.x, y = self.y)
    
    def __str__(self):
        return (f"Position: {self.x},{self.y}")

class Agent():
    pass

    def __init__(self):
        self.state = State()
        
    def take_action(self, action = None):
        act = rand.choice(["left", "right", "up", "down"])
        return act 
 
class MDP(list):
    """ Class that represents an episodic Markov Decision Process, aka "task" """
    S = []          # set of states
    A = []          # set of actions
    P = None        # transition function that gives the probability of moving to a new state
    R = None        # a reward function that gives the immediate reward for taking an action in a state.
    S_0 = []        #  distribution over starting states
    S_f = []        # set of terminal states
    agent = Agent()
    
    # F..
    grid_size = GridSize()
    
    
    
    def __init__(self, init_state = None, features : Features = None, run_with_print = False):
        self.agent = Agent()
        
        # initial state
        if init_state == None:
            self.init_state = State()
        else:
            self.init_state = init_state
        self.run_with_print = run_with_print    
        
        # connect a Grid to the mdp
        self.grid = Grid()
        
        # features
        self.grid_size = features[GridSize().get_feature_name()]
        self.test_feat = TestFeat()
        if features == None:
            self.features = [self.grid_size, self.test_feat]
        else: 
            self.features = features
            self.features.mdp = self
            if run_with_print:
                self.features.run_with_print = True
        self.attach_features()
    
    def attach_features(self):
        self.grid.size = (self.grid_size.width, self.grid_size.height)
        # self.grid.hole = HoleObj()
        print(f"does hole exist? {self.features.get_feature(Hole()).exists}")
        self.grid.add_object(HoleObj(self.features[Hole().get_feature_name()].width, exists = self.features[Hole().get_feature_name()].exists))
        self.grid.add_object(KeyObj(exists = True))
        self.grid.add_object(LockObj(exists = True))
        self.features.run_dependencies()
    
    def P(self, state : State, action : str) -> list[tuple[State, float]] :# transition function
        """ Transition function """
        sa        = SA(state, action)
        new_state = state.copy()
        
        new_pos   = sa.move(mdp = self)
        
        # what happens at new pos?
        new_state = new_pos
        
        # currently always sure?
        p = 1
        
        self.agent.state = new_state
        self.state = new_state
        
        return [(new_state, p)]

    def transition(self, state : State, action : str):
        return self.P(state, action)

    def R(self, state : State, action : str) -> float:
        """ Reward function """
        sa        = SA(state, action)
        new_state = state.copy()
        
        new_pos   = sa.move(mdp = self)
        
        # reward at new_pos
        reward = 0
        
                
        return reward
        
    def check_grid_boundaries(self, state_action : SA):
        pass
        
    def define_all_states(self):
        pass
    
    def __str__(self):
        
        string = "MDP with: \n  Grid size: {0}".format(self.grid_size)
        return string


class SA():

    def __init__(self, state : State, action):
        self.state = state
        self.action = action


    def move(self, mdp : MDP) -> State:
        """ Returns a new state from movement - checks mdp boundaries """
        new_state = self.state.copy()
        # Left
        if self.action == "left" or self.action ==  3:
            if new_state.x <= 0:
                return new_state
            new_state.x -= 1            
        
        # Right
        if self.action == "right" or self.action == 1:
            if new_state.x >= mdp.grid_size.width:
                return new_state
            new_state.x += 1            
        
        # Up
        if self.action == "up" or self.action == 0:
            if new_state.y <= 0:
                return new_state
            new_state.y -= 1            

        # Down
        if self.action == "down" or self.action == 2:
            if new_state.y >= mdp.grid_size.height:
                return new_state
            new_state.y += 1            
        
        
        return new_state

    def check_grid_boundaries(self, state_action : SA):
        pass
        
