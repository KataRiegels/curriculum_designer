from __future__ import annotations

from grid_representation import *
from features import *
import random as rand
import math
import statistics as st
import copy

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

    def __str__(self):
        
        # beams = st.mean(self.beams_sensor)
        # key = st.mean(self.key_sensor)
        # lock = st.mean(self.lock_sensor)
        # pit = any(self.hole_sensor)
        beams = min(self.beams_sensor)
        key = min(self.key_sensor)
        lock = min(self.lock_sensor)
        pit = any(self.hole_sensor)
        
        
        return (f"beams: {beams},key: {key}, lock: {lock}, pit: {pit}, {self.key_found} ---- ")
    def __repr__(self):
        return self.__str__()
    # def __str__(self):
        
        
    #     beams = (self.beams_sensor)
    #     key =(self.key_sensor)
    #     lock = (self.lock_sensor)
    #     pit = (self.hole_sensor)
        
        
    #     return (f"beams: {beams},key: {key}, lock: {lock}, pit: {pit}, {self.key_found} ---- ")

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
    
    @property
    def position(self):
        return self.coordinate
    
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
    
    def update_sensors(self, grid : Grid):
        """ Updates the different agent sensors, e.g. key distance"""
        hole_sensor = []; beams_sensor = []
        key_sensor = [];  lock_sensor = []
        
        # Update sensors from each possible action
        for action in ["up", "down", "left", "right"]:
            # Get a state from moving
            new_state = SA(self, action).move(grid)
            
            # Update sensors based off of current action
            hole_distance = grid.is_hole_adjacent(new_state.coordinate)
            beams_distance = grid.distance_to_nearest(agent=new_state.coordinate, sensor_type='beams')
            key_distance = grid.distance_to_nearest(agent=new_state.coordinate, sensor_type='key')
            lock_distance = grid.distance_to_nearest(agent=new_state.coordinate, sensor_type='lock')
            
            hole_sensor.append(hole_distance)
            beams_sensor.append(beams_distance)
            key_sensor.append(key_distance)
            lock_sensor.append(lock_distance)
        
        self.hole_distance = grid.distance_to_nearest(agent=self.coordinate, sensor_type='hole')
        self.beams_distance = grid.distance_to_nearest(agent=self.coordinate, sensor_type='beams')
        self.key_distance = grid.distance_to_nearest(agent=self.coordinate, sensor_type='key')
        self.lock_distance = grid.distance_to_nearest(agent=self.coordinate, sensor_type='lock')
        
        # Add to the state's sensors    
        self.key_sensor = key_sensor    
        self.lock_sensor = lock_sensor
        self.hole_sensor = hole_sensor
        self.beams_sensor = beams_sensor
        
    
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
        return (f"Position: {self.x},{self.y}, beams: {self.beams_distance}, pit: {self.hole_distance} ---- ")
    def __repr__(self):
        return self.__str__()
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
    if (state.hole_distance == 0.0):
        # print(f'sensors are: {state.sensors}')
        # print(f'state is: {state}')
        # print(f'HOLEEEEE')
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
    
    def copy(self):
        mdp_copy = copy.deepcopy(self)
        return mdp_copy
    
    def __init__(self, init_state = None, features : Features = None, terminations = [], run_with_print = False):
        
        
        # set the initial state
        if    init_state == None: self.init_state = State()
        else:                     self.init_state = init_state
        self.agent = Agent(self.init_state)
        
        self.init_attributes = [self.init_state.copy(), features, terminations.copy()]

        self.mdp_ended = False; self.term_cause = "nothing"; self.interaction_number = 0

        # MDP termination things
        self.terminations = terminations
        if len(terminations) == 0:
            self.terminations.append(termination_pit)
        if len(terminations) == 1:
            self.terminations.append(termination_lock)
        
        self.specific_reward_values = {} 
        self.terminal_states = None
        
        # Initialize the Grid
        self.grid = Grid()
        
        # initialize mdp agent
        
        self.target_task = None
        self.task_type = None
        
        self.run_with_print = run_with_print    
        
        # features
        self.features = features
        # self.features.mdp = self
        if run_with_print:
            self.features.run_with_print = True
        self.attach_features()
        
        
        
        self.random_mdp_num = rand.randint(0, 100)
        # self.initial_mdp = self.copy()
        
            
    def reset_mdp(self):
        init_mdp = MDP(init_state=self.init_attributes[0], features=self.init_attributes[1], terminations=self.init_attributes[2])
        init_mdp.target_task = self.target_task
        init_mdp.task_type = self.task_type
        return init_mdp
        # initial_mdp_copy = self.initial_mdp.copy()
        # print(f'Resetting MDP with {initial_mdp_copy}')
        # return initial_mdp_copy
    
    def update_state(self):
        """Updates every run_mdp loop"""
        self.agent.state.update_sensors(self.grid)
        self.interaction_number += 1
    
    def attach_features(self):
        """Attached features to the MDP - includes adding features to the corresponding grid"""
        self.grid.size = (self.features[GridSize().get_feature_name()].width, self.features[GridSize().get_feature_name()].height)
        self.grid.add_object(HoleObj(self.features[Hole().get_feature_name()].width, exists = self.features[Hole().get_feature_name()].exists))
        self.grid.add_object(KeyObj(exists = True))
        self.grid.add_object(LockObj(exists = True))
        self.agent.state.update_sensors(self.grid)
        # self.features.run_dependencies()
    
    def P(self, state : State, action : str) -> list[tuple[State, float]] :# transition function
        """ Transition function """
        new_state = self.move(state, action)
        
        # sa        = SA(state, action)
        # new_state = state.copy()
        # new_state   = sa.move(self.grid)
        
        # Handles removal of key when picked up
        cell_type = self.grid.check_coordinate((new_state.coordinate))
        if cell_type == "key" and not self.agent.state.key_found:
            self.agent.state.key_found = True
            new_state.key_found = True
            self.grid.assign_cell(new_state.coordinate, None)        
        
        # check for terminal states
        self.check_termination(new_state)

        
        # currently always sure?
        p = 1
        
        
        return [(new_state, p)]

    def take_action(self, action):
        """Handles all the things related to taking an action for an MDP"""
        
        reward     = self.R(self.agent.state, action)
        next_state = self.P(self.agent.state, action)[0][0]
        done       = self.mdp_ended

        self.agent.state = next_state
        self.update_state()
        
        
        return next_state, reward, done


    def end_mdp(self, cause = None):
        """ Call to end current mdp due to termination """
        self.mdp_ended = True
        self.term_cause = cause
        return True
    
    def check_termination(self, state : State):
        """Checks whether the given state should cause MDP termination"""
        # When specific terminal states are given
        if self.terminal_states:
            for term_state in self.terminal_states:
                if state.sensors == term_state:
                    self.end_mdp(str(state))
                    return
                    
        # Runs the general termination states
        for func in self.terminations:
            term_cause = func(state)
            if term_cause:
                # print(f'def term: {term_cause}')
                self.end_mdp(cause=term_cause)
        
        



    
    
    def R(self, state : State, action : str, values = None) -> float:
        """ Reward function """
        # sa        = SA(state, action)
        # new_state = state.copy()
        new_state = self.move(state, action)
        
        
        # new_state   = sa.move(self.grid)
        reward = 0
        
        # Checks for possible given terminal states outside the basic pit and lock
        key = (state.sensors, action, new_state.sensors)
        if key in self.specific_reward_values:        
            reward = self.specific_reward_values[(state.sensors, action, new_state.sensors)]
        else:
            reward = self.immediate_reward(new_state, self.grid)
                    
        return reward*(1)

    @staticmethod        
    def immediate_reward(state, grid):
        """ Reward based off the cell type """ 
        reward = 0
        cell_type = grid.check_coordinate((state.coordinate))
        if cell_type == "key":
            reward = 500
        elif cell_type == "hole" :
            reward = -200
        elif cell_type == "lock" and state.key_found == True:
            reward = 1000
        else:
            reward = -10
        return reward
    
    def move(self, state, action) -> State:
        """ Returns a new state from movement - checks mdp boundaries """
        new_state = state.copy()
        # Left
        if action == "left" or action ==  3:
            if new_state.x <= 0:
                return new_state
            new_state.x -= 1            
        
        # Right
        if action == "right" or action == 1:
            if new_state.x >= self.grid.width - 1:
                return new_state
            new_state.x += 1            
        
        # Up
        if action == "up" or action == 0:
            if new_state.y <= 0:
                return new_state
            new_state.y -= 1            

        # Down
        if action == "down" or action == 2:
            if new_state.y >= self.grid.height - 1:
                return new_state
            new_state.y += 1            
        
        # if action ==''
        new_state.update_sensors(self.grid)
        return new_state
    
    def get_action_space(self, state):
        # new_state = self.agent.state.copy()
        new_state = state
        action_space = []
        for action in range(4):
            # Left
            if action == "left" or action ==  3:
                if not new_state.x <= 0:
                    action_space.append(action)
            
            # Right
            if action == "right" or action == 1:
                if not new_state.x >= self.grid.width - 1:
                    action_space.append(action)
            # Up
            if action == "up" or action == 0:
                if not new_state.y <= 0:
                    action_space.append(action)

            # Down
            if action == "down" or action == 2:
                if not new_state.y >= self.grid.height - 1:
                    action_space.append(action)
        return action_space
    def __str__(self):
        """How the class is represented when e.g. printed"""
        string = f"MDP: (((# {self.random_mdp_num} - size({self.grid.size}) - pit({self.grid.hole}) - type: ({self.task_type}) )))"
        return string

    def __repr__(self):
        return self.__str__()
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
        # new_state.update_sensors(grid)
        return new_state
