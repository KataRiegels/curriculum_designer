from __future__ import annotations

# from agent import Agent
from grid_representation import *
from features import *
import random as rand

class State():
    def __init__(self, x = 0, y = 0, key_found = False):
        self.x = x
        self.y = y
        self.key_found = key_found
        self.hole_sensor = []
        self.beams_sensor = []
        self.key_sensor = []
        self.lock_sensor = []
    
    def update_key_sensors(self):
        pass
        

        
    def position(self):
        return (self.x, self.y)
    
    @property
    def coordinate(self):
        return (self.x,self.y)
    
    def copy(self):
        new_state = State(x=self.x, y=self.y, key_found=self.key_found)
        new_state.hole_sensor = self.hole_sensor.copy()
        new_state.beams_sensor = self.beams_sensor.copy()
        new_state.key_sensor = self.key_sensor.copy()
        new_state.lock_sensor = self.lock_sensor.copy()
        return new_state
    
    def __str__(self):
        return (f"Position: {self.x},{self.y} ---- ")

class Agent():
    pass

    def __init__(self, state : State = None):
        if state != None: self.state = state
        else: self.state = State()

    def update_sensors(self, grid : Grid):
        
        hole_sensor = []
        beams_sensor = []
        keý_sensor = []
        lock_sensor = []
        
        # left
        for action in ["up", "down", "left", "right"]:
            new_state = SA(self.state, action).move(grid)
            hole_distance = grid.is_hole_adjacent(new_state.coordinate)
            beams_distance = grid.distance_to_nearest(agent=new_state.coordinate, sensor_type='beams')
            key_distance = grid.distance_to_nearest(agent=new_state.coordinate, sensor_type='key')
            lock_distance = grid.distance_to_nearest(agent=new_state.coordinate, sensor_type='lock')
            
            
            
            hole_sensor.append(hole_distance)
            beams_sensor.append(beams_distance)
            keý_sensor.append(key_distance)
            lock_sensor.append(lock_distance)
        self.state.key_sensor = keý_sensor    
        self.state.lock_sensor = lock_sensor
        # self.state.hole_sensor = hole_sensor
        self.state.beams_sensor = beams_sensor
        

# Update the corresponding attributes in your State class
        # mdp.agent.state.key_sensor = [key_distance]
# Similarly, update other attributes based on their corresponding distances

        
        pass
    
    @property
    def coordinate(self):
        return (self.state.x, self.state.y)
        
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
    
    def copy(self):
        return MDP(init_state = self.init_state, features = self.features, run_with_print = self.run_with_print)
    
    def __init__(self, init_state = None, features : Features = None, run_with_print = False):
        self.agent = Agent(State(1,7))
        self.mdp_ended = False
        # initial state
        if init_state == None:
            self.init_state = State()
        else:
            self.init_state = init_state
        self.run_with_print = run_with_print    
        
        # connect a Grid to the mdp
        self.grid = Grid()
        self.term_cause = "nothing"
        # features
        self.grid_size = features[GridSize().get_feature_name()]
        if features == None:
            self.features = [self.grid_size, self.test_feat]
        else: 
            self.features = features
            self.features.mdp = self
            if run_with_print:
                self.features.run_with_print = True
        self.attach_features()
        
        self.interaction_number = 0
        
        self.random_mdp_num = rand.randint(0, 100)
    
    def update_state(self):
        self.interaction_number += 1
    
    def attach_features(self):
        self.grid.size = (self.grid_size.width, self.grid_size.height)
        # self.grid.hole = HoleObj()
        self.grid.add_object(HoleObj(self.features[Hole().get_feature_name()].width, exists = self.features[Hole().get_feature_name()].exists))
        self.grid.add_object(KeyObj(exists = True))
        self.grid.add_object(LockObj(exists = True))
        self.features.run_dependencies()
    
    def P(self, state : State, action : str) -> list[tuple[State, float]] :# transition function
        """ Transition function """
        sa        = SA(state, action)
        new_state = state.copy()
        
        new_pos   = sa.move(self.grid)
        
        # what happens at new pos?
        new_state = new_pos
        # self.agent.state = new_state
        
        cell_type = self.grid.check_coordinate((new_state.coordinate))
        if cell_type == "key" and not self.agent.state.key_found:
            self.agent.state.key_found == True
            new_state.key_found = True
            self.grid.assign_cell(new_state.coordinate, None)        
            print("Key found")
        
        # currently always sure?
        p = 1
        
        self.state = new_state
        
        self.check_termination(new_state)
        self.agent.update_sensors(self.grid)
        return [(new_state, p)]

    def transition(self, state : State, action : str):
        return self.P(state, action)

    def end_mdp(self, cause = None):
        self.mdp_ended = True
        self.term_cause = cause
        print(f'Number of interactions: {self.interaction_number} due to {cause}')
        # self.interaction_number = 0
        return True

    def check_termination(self, state):
        current_cell_type = self.grid.check_coordinate((state.coordinate))
        if (current_cell_type == "hole" \
                or current_cell_type == "lock" and state.key_found):
            self.end_mdp(cause = current_cell_type)            
    
    def R(self, state : State, action : str) -> float:
        """ Reward function """
        sa        = SA(state, action)
        new_state = state.copy()
        
        new_state   = sa.move(self.grid)
        reward = 0
        cell_type = self.grid.check_coordinate((new_state.coordinate))
        if cell_type == "key":
            reward == 500
        elif cell_type == "hole" :
            reward = -200
        elif cell_type == "lock" and state.key_found == True:
            print(f'Unlocked lock with key!')
            reward = 1000
        else:
            reward = -10
            
        reward = 0
        
        # reward at new_pos
        # reward = 0
        
                
        return reward
        
    def check_grid_boundaries(self, state_action : SA):
        pass
        
    def define_all_states(self):
        pass
    
    def __str__(self):
        
        string = "MDP with: \n MDP number {0} \n  Grid size: {1}".format(self.random_mdp_num, self.grid_size)
        return string


class SA():

    def __init__(self, state : State, action):
        self.state = state
        self.action = action


    def move(self, grid : Grid) -> State:
        """ Returns a new state from movement - checks mdp boundaries """
        new_state = self.state.copy()
        # Left
        if self.action == "left" or self.action ==  3:
            if new_state.x <= 0:
                return new_state
            new_state.x -= 1            
        
        # Right
        if self.action == "right" or self.action == 1:
            if new_state.x >= grid.width - 1:
                return new_state
            new_state.x += 1            
        
        # Up
        if self.action == "up" or self.action == 0:
            if new_state.y <= 0:
                return new_state
            new_state.y -= 1            

        # Down
        if self.action == "down" or self.action == 2:
            if new_state.y >= grid.height - 1:
                return new_state
            new_state.y += 1            
        
        
        return new_state

    def check_grid_boundaries(self, state_action : SA):
        pass
        
