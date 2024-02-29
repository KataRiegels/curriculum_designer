from __future__ import annotations

# from agent import Agent
from grid_representation import *
from features import *
import random as rand


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
        
    def __hash__(self):
        # Use a tuple of the relevant attributes for hashing
        return hash((self.key_found, tuple(self.hole_sensor), tuple(self.beams_sensor),
                     tuple(self.key_sensor), tuple(self.lock_sensor)))
        
    @staticmethod    
    def convert_to_loadable( data):
        returner = State(data[0], data[1], data[2], data[3], data[4])
        return returner

    def to_np_save(self):
        # Assuming loaded_data is a dictionary or structure obtained from np.load
        state_logger =        ( self.key_found, tuple(self.hole_sensor), tuple(self.beams_sensor),
                     tuple(self.key_sensor), tuple(self.lock_sensor))
        return state_logger
    pass

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
        keý_sensor = [];  lock_sensor = []
        
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
            keý_sensor.append(key_distance)
            lock_sensor.append(lock_distance)
        
        
        # Add to the state's sensors    
        self.state.key_sensor = keý_sensor    
        self.state.lock_sensor = lock_sensor
        self.state.hole_sensor = hole_sensor
        self.state.beams_sensor = beams_sensor
        
    
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
        
        # set the initial state
        if init_state == None:
            self.init_state = State()
        else:
            self.init_state = init_state
        
        # initialize mdp agent
        self.agent = Agent(self.init_state)
        
        # Initialize the Grid
        self.grid = Grid()
        
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
        self.interaction_number += 1
    
    def attach_features(self):
        """Attached features to the MDP - includes adding features to the corresponding grid"""
        self.grid.size = (self.features[GridSize().get_feature_name()].width, self.features[GridSize().get_feature_name()].height)
        self.grid.add_object(HoleObj(self.features[Hole().get_feature_name()].width, exists = self.features[Hole().get_feature_name()].exists))
        self.grid.add_object(KeyObj(exists = True))
        self.grid.add_object(LockObj(exists = True))
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
            print("Key found")
        
        # check for terminal states
        self.check_termination(new_state)
        
        # currently always sure?
        p = 1
        
        
        self.agent.update_sensors(self.grid)
        return [(new_state, p)]

    def transition(self, state : State, action : str):
        return self.P(state, action)

    def end_mdp(self, cause = None):
        """ Call to end current mdp due to termination """
        self.mdp_ended = True
        self.term_cause = cause
        print(f'Number of interactions: {self.interaction_number} due to {cause}')
        return True

    def check_termination(self, state):
        """ checks and handles when a state leads to termination """
        current_cell_type = self.grid.check_coordinate((state.coordinate))
        
        # Agent fell into the pit or unlocked the lock
        if (current_cell_type == "hole" \
                or current_cell_type == "lock" and state.key_found):
            self.end_mdp(cause = current_cell_type)            
    
    def R(self, state : State, action : str) -> float:
        """ Reward function """
        sa        = SA(state, action)
        new_state = state.copy()
        
        new_state   = sa.move(self.grid)
        reward = 0
        
        # Reward based off the cell type
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
        
        
        return new_state
