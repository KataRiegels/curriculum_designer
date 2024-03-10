from __future__ import annotations

from grid_representation import *
from features import *
import random as rand
import math
import statistics as st

class Sensors():
    """ Class that essentially just keeps the sensor part of a state"""
    def __init__(self, key_found,
            hole_sensor ,
            beams_sensor ,
            key_sensor ,
            lock_sensor ):
        self.key_found = key_found
        self.hole_sensor = hole_sensor
        self.beams_sensor = beams_sensor
        self.key_sensor = key_sensor
        self.lock_sensor = lock_sensor
        
    def eq(self, other_state):
        """Determine if two states are equal"""
        
        eq = (
            self.key_found == other_state.key_found and
            self.hole_sensor == other_state.hole_sensor and
            self.beams_sensor == other_state.beams_sensor and
            self.key_sensor == other_state.key_sensor and
            self.lock_sensor == other_state.lock_sensor
        )
        return eq 


    def __eq__(self, other):
        """Overwriting '==' operator"""
        return self.eq(other)  
    def __hash__(self):
        """Use a tuple of the relevant attributes for hashing"""
        return hash((self.key_found, tuple(self.hole_sensor), tuple(self.beams_sensor),
                     tuple(self.key_sensor), tuple(self.lock_sensor)))
        
    @staticmethod    
    def convert_to_loadable( data):
        """Crates a structure that can be saved in .npy file"""
        converted_data = [list(item) if isinstance(item, (tuple, list)) else item for item in data]
        returner = Sensors(*converted_data)
        return returner

    def to_np_save(self):
        """Lets you load .npy files and convert the data structure to a Sensor"""
        state_logger =        ( self.key_found, tuple(self.hole_sensor), tuple(self.beams_sensor),
                     tuple(self.key_sensor), tuple(self.lock_sensor))
        return state_logger
    pass

    # def __str__(self):
        
    #     beams = st.mean(self.beams_sensor)
    #     key = st.mean(self.key_sensor)
    #     lock = st.mean(self.lock_sensor)
    #     pit = any(self.hole_sensor)
        
        
    #     return (f"{beams},{key}, {lock}, {pit}, {self.key_found} ---- ")

    def __str__(self):
        
        
        beams = (self.beams_sensor)
        key =(self.key_sensor)
        lock = (self.lock_sensor)
        pit = (self.hole_sensor)
        
        
        return (f"{beams},{key}, {lock}, {pit}, {self.key_found} ---- ")

class State():
    """Represents position and sensors """
    def __init__(self, x = 0, y = 0, key_found = False,
                hole_sensor = [] ,
                beams_sensor = [],
                key_sensor = [],
                lock_sensor = []):
        self.x = x
        self.y = y
        self.key_found = key_found
        self.hole_sensor = hole_sensor
        self.beams_sensor = beams_sensor
        self.key_sensor = key_sensor
        self.lock_sensor = lock_sensor
        self.hole_distance = None
        self.beams_distance = None
        self.key_distance = None
        self.lock_distance = None
        
    
    @property
    def distances(self):
        pass
    
    @property        
    def sensors(self):
        """Get a sensor object from the State"""
        return Sensors(self.key_found,
            self.hole_sensor ,
            self.beams_sensor ,
            self.key_sensor ,
            self.lock_sensor ,
        )
        
    @property
    def coordinate(self):
        return (self.x,self.y)
    
    def copy(self):
        """Copying the State"""
        new_state = State(x=self.x, y=self.y, key_found=self.key_found)
        new_state.hole_sensor = self.hole_sensor.copy()
        new_state.beams_sensor = self.beams_sensor.copy()
        new_state.key_sensor = self.key_sensor.copy()
        new_state.lock_sensor = self.lock_sensor.copy()
        new_state.hole_distance = self.hole_distance
        new_state.beams_distance = self.beams_distance
        new_state.key_distance = self.key_distance
        new_state.lock_distance = self.lock_distance
        return new_state
    
    
    
    def eq(self, other_state):
        """Determine if two states are equal"""
        return (
            self.x == other_state.x and
            self.y == other_state.y and
            self.key_found == other_state.key_found and
            self.hole_sensor == other_state.hole_sensor and
            self.beams_sensor == other_state.beams_sensor and
            self.key_sensor == other_state.key_sensor and
            self.lock_sensor == other_state.lock_sensor
        )

    def __eq__(self, other):
        """Overwriting '==' operator"""
        if not isinstance(other, State):
            return False
        return self.eq(other)
    
    def __hash__(self):
        """When using hashing, it uses the below as the key"""
        # Use a tuple of the relevant attributes for hashing
        return hash((self.x, self.y, self.key_found, tuple(self.hole_sensor), tuple(self.beams_sensor),
                     tuple(self.key_sensor), tuple(self.lock_sensor)))

    def __str__(self):
        return (f"Position: {self.x},{self.y} ---- ")

    def convert_to_loadable(self, data):
        """ Returning structure for saving in .npy"""
        returner = State(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
        return returner

    def to_np_save(self):
        """ Loading from structure in .npy"""
        # Assuming loaded_data is a dictionary or structure obtained from np.load
        state_logger =        (self.x, self.y, self.key_found, tuple(self.hole_sensor), tuple(self.beams_sensor),
                     tuple(self.key_sensor), tuple(self.lock_sensor))
        return state_logger
    
    
class Agent():
    """ The agent that needs to solve the task"""
    def __init__(self, state : State = None):
        if state != None: self.state = state
        else: self.state = State()

    def update_sensors(self, grid : Grid):
        """ Updates the different agent sensors, e.g. key distance"""
        hole_sensor = []; beams_sensor = []
        key_sensor = [];  lock_sensor = []
        
        # Update sensors from each possible action
        for action in ["up", "down", "left", "right"]:
            # Get a state from moving
            new_state = SA(self.state, action).move(grid)
            
            # Update sensors based off of current action
            hole_distance = grid.is_hole_adjacent(new_state.coordinate)
            beams_distance = grid.distance_to_nearest(agent=new_state.coordinate, sensor_type='beams')
            key_distance = grid.distance_to_nearest(agent=new_state.coordinate, sensor_type='key')
            lock_distance = grid.distance_to_nearest(agent=new_state.coordinate, sensor_type='lock')
            
            hole_sensor.append(hole_distance)
            beams_sensor.append(beams_distance)
            key_sensor.append(key_distance)
            lock_sensor.append(lock_distance)
        
        self.state.hole_distance = grid.distance_to_nearest(agent=self.state.coordinate, sensor_type='hole')
        self.state.beams_distance = grid.distance_to_nearest(agent=self.state.coordinate, sensor_type='beams')
        self.state.key_distance = grid.distance_to_nearest(agent=self.state.coordinate, sensor_type='key')
        self.state.lock_distance = grid.distance_to_nearest(agent=self.state.coordinate, sensor_type='lock')
        
        
        # Add to the state's sensors    
        self.state.key_sensor = key_sensor    
        self.state.lock_sensor = lock_sensor
        self.state.hole_sensor = hole_sensor
        self.state.beams_sensor = beams_sensor
        
    
    @property
    def coordinate(self):
        return (self.state.x, self.state.y)
        
    def take_action(self, action = None):
        act = rand.choice(["left", "right", "up", "down"])
        return act 
 
def termination_key(state : State):
    if state.key_distance == 0.0:
        return "key"
    else:
        return False    
    
def termination_pit(state : State):
    # print(f'pit termination??')
    if (state.hole_distance == 0.0):
        if state.key_found:
            return "holekey"
        return "hole"
    else:
        return False    

def termination_lock(state : State):
    if state.lock_distance == 0.0 and state.key_found:
        return "lock"
    else:
        return False    



 
 
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
    
    def __init__(self, init_state = None, features : Features = None, run_with_print = False, terminations = []):
        
        # set the initial state
        if init_state == None:
            self.init_state = State()
        else:
            self.init_state = init_state
        
        self.terminations = terminations
        if len(terminations) == 0:
            self.terminations.append(termination_pit)
        if len(terminations) == 1:
            self.terminations.append(termination_lock)
        # else: 
        #     for t_cause in terminations:
        #         self.terminations.append(t_cause)
        self.q_agent = None
        
        # Initialize the Grid
        self.grid = Grid()
        
        # initialize mdp agent
        self.agent = Agent(self.init_state)
        
        # Keep track of whether the MDP episode should terminate.
        self.mdp_ended = False
        
        self.run_with_print = run_with_print    
        
        # Initializing the term_cause which is nothing to begin with
        self.term_cause = "nothing"
        
        # features
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
        """Updates every run_mdp loop"""
        self.agent.update_sensors(self.grid)
        self.interaction_number += 1
    
    def attach_features(self):
        """Attached features to the MDP - includes adding features to the corresponding grid"""
        self.grid.size = (self.features[GridSize().get_feature_name()].width, self.features[GridSize().get_feature_name()].height)
        self.grid.add_object(HoleObj(self.features[Hole().get_feature_name()].width, exists = self.features[Hole().get_feature_name()].exists))
        self.grid.add_object(KeyObj(exists = True))
        self.grid.add_object(LockObj(exists = True))
        self.agent.update_sensors(self.grid)
        # self.features.run_dependencies()
    
    def P(self, state : State, action : str) -> list[tuple[State, float]] :# transition function
        """ Transition function """
        sa        = SA(state, action)
        new_state = state.copy()
        new_state   = sa.move(self.grid)
        
        
        # Handles removal of key when picked up
        cell_type = self.grid.check_coordinate((new_state.coordinate))
        if cell_type == "key" and not self.agent.state.key_found:
            self.agent.state.key_found == True
            new_state.key_found = True
            self.grid.assign_cell(new_state.coordinate, None)        
        
        # check for terminal states
        self.check_termination_2(new_state)
        # self.check_termination(new_state)

        
        # currently always sure?
        p = 1
        
        
        return [(new_state, p)]

    def take_action(self, action):
        reward = self.R(self.agent.state, action)
        next_state = self.P(self.agent.state, action)[0][0]
        done = self.mdp_ended

        self.agent.state = next_state
        self.update_state()
        
        
        
        return next_state, reward, done
        pass

    def transition(self, state : State, action : str):
        return self.P(state, action)

    def end_mdp(self, cause = None):
        """ Call to end current mdp due to termination """
        self.mdp_ended = True
        self.term_cause = cause
        return True
    def check_termination_2(self, state):
        current_cell_type = self.grid.check_coordinate(state.coordinate)
        for func in self.terminations:
            term_cause = func(state)
            if term_cause:
                self.end_mdp(cause=term_cause)
                return       
        # while (term == False):        
        # if term == ("lock"):
        # Agent fell into the pit or unlocked the lock
        # if (current_cell_type == "hole" and state.key_found):
        #     self.end_mdp(cause = "holekey")            
            
        # elif (current_cell_type == "hole"):
        #     self.end_mdp(cause = current_cell_type)
              
        # elif (current_cell_type == "lock" and state.key_found):
        #     self.end_mdp(cause = current_cell_type)




                        
    def check_termination(self, state):
        """ checks and handles when a state leads to termination """
        current_cell_type = self.grid.check_coordinate((state.coordinate))
        
        # Agent fell into the pit or unlocked the lock
        if (current_cell_type == "hole" and state.key_found):
            print(f'term1')
            self.end_mdp(cause = "holekey")            
            
        elif (current_cell_type == "hole" \
                or current_cell_type == "lock" and state.key_found):
            print(f'term1')
            self.end_mdp(cause = current_cell_type)            
    
    # def termination_lock(self, state):
    #     current_cell_type = self.grid.check_coordinate((state.coordinate))
    #     if (current_cell_type == "lock" and state.key_found):
    #         self.end_mdp(cause = current_cell_type)            
        
    
    # def termination_pit(self, state):
    #     current_cell_type = self.grid.check_coordinate((state.coordinate))
    #     if (current_cell_type == "hole"):
    #         if state.key_found:
    #             self.end_mdp(cause = "holekey")
    #         else: 
    #             self.end_mdp(cause = current_cell_type)            
    
    # def termination_lock(self, state):
    #     pass    
    
    def R(self, state : State, action : str) -> float:
        """ Reward function """
        sa        = SA(state, action)
        new_state = state.copy()
        
        new_state   = sa.move(self.grid)
        reward = 0
        
        reward = self.value_function(new_state, self.grid)
                
        return reward*(1)

    @staticmethod        
    def value_function(state, grid):
        # Reward based off the cell type
        reward = 0
        cell_type = grid.check_coordinate((state.coordinate))
        if cell_type == "key":
            reward == 500
        elif cell_type == "hole" :
            reward = -200
        elif cell_type == "lock" and state.key_found == True:
            reward = 1000
        else:
            reward = -10
        return reward
        
    def __str__(self):
        """How the class is represented when e.g. printed"""
        string = "MDP with: \n MDP number {0} \n  Grid size: {1}".format(self.random_mdp_num, self.grid_size)
        return string


class SA():
    """Not to be confused with the assault. stands for state-action"""
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
        
        # if self.action ==''
        return new_state
