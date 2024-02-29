import sys
import os
path = os.path.abspath("domains")
# path = os.path.abspath("algorithm")
sys.path.append(path)
# from ..domains.M import *
print("--SCRIPT STARTING")
from algorithm.q_learning import *
from domains.features import *
from domains.mdp import *
from domains.task_generators import *
from domains.grid_world import *
import time
import threading
import csv
import pandas as pd
import matplotlib.pyplot as plt
from logger import Plotter, Logger, CsvManager

stop_event = threading.Event()
reset_event = threading.Event()

# creates target task and simplified version
feature_vector = Features(GridSize(), Hole(exists = True))
old_mdp = MDP(features = feature_vector, run_with_print=True)
mdp = task_simplification(MDP(features = feature_vector, run_with_print=True))


q_agent = QLearningAgent(10000, 5000000, (mdp.grid.height * mdp.grid.width), 4, 0.1, 0.9, 0.2)

use_pg = True



class Tracker():
    
    
    def __init__(self, mdp : MDP, stop_event, reset_event, q_agent, logger, load_q = False):
        self.q_agent = q_agent
        self.mdp = mdp
        self.logger = logger
        
        self.stop_event = stop_event
        self.reset_event = reset_event
        self.pg = PygameInstance()
        self.pg.mdp = self.mdp
        self.generation_manager = []
        self.generation = 0
        self.reward_logger = []
        
        self.information_parser = {}
        
        self.pg.information_parser = self.information_parser
        self.information_parser["fails"] = 0
        self.information_parser["successes"] = 0
        self.information_parser["keys"] = 0
        
        self.actions_logger = {
            "up" : 0,
            "right" : 0,
            "down" : 0,
            "left" : 0,
        }
        self.information_parser["action log"] = self.actions_logger
        
        self.q_values_log = []
        
        if load_q:
            q_values = self.logger.load_q_values_log()
            self.q_agent.q_values = q_values
            
    
    def run_mdp(self):
        
        
        self.mdp_copy = self.mdp.copy()
        accu_reward = 0
        while not self.stop_event.is_set():

            time.sleep(.1)
            
            # Current state before moving
            current_state = self.mdp.agent.state.copy()
            current_sensors = current_state.sensors
            
            
            # Decide the action to take
            action = self.q_agent.choose_action(current_sensors)
            
            # gibberish to keep track of how often actions are taken : delete?
            if action == 0:
                self.actions_logger['up'] += 1
            elif action == 1:  
                self.actions_logger['right'] += 1
            elif action == 2:  
                self.actions_logger['down'] += 1
            elif action == 3:  
                self.actions_logger['left'] += 1
            
            
            # Update the agent's state
            self.mdp.agent.state = self.mdp.P(self.mdp.agent.state, action)[0][0]
            self.mdp.update_state()
            
            # specify new state/sensors
            new_state = self.mdp.agent.state
            new_sensors = new_state.sensors
            
            # old_q_value = self.q_agent.get_q_value(current_state, action)
            old_q_value = self.q_agent.get_q_value(current_sensors, action)
            
            # calculate reward corresponding to taking the decided action
            reward = self.mdp.R(current_state, action)
            accu_reward += reward
            
            # Calculate new q value
            # new_q_value = old_q_value + self.q_agent.learning_rate * (reward + self.q_agent.discount_factor * max(self.q_agent.get_q_value(new_state.coordinate, a) for a in range(self.q_agent.action_space_size)) - old_q_value)
            new_q_value = old_q_value + \
                self.q_agent.learning_rate * (
                    reward +
                    self.q_agent.discount_factor * max(
                        # self.q_agent.get_q_value(new_state, a) 
                        self.q_agent.get_q_value(new_sensors, a) 
                        for a in range(self.q_agent.action_space_size)
                    ) - old_q_value
                )
                
            # Update new q value for the coreespinding state and action
            self.q_agent.update_q_value(new_sensors, action, new_q_value)


            # If the MDP ended (aka agent reached terminal state)
            if self.mdp.mdp_ended == True:
                print("Restarting MDP")
                
                # update reward logger and data to be able to plot it later
                self.reward_logger.append(reward)
                reward_data = [self.generation, accu_reward, self.mdp.term_cause ]
                accu_reward = 0
                
                # update data iteration to be able to plot it later
                term_data = [self.generation, self.mdp.interaction_number, self.mdp.term_cause ]
                
                # Might be removable?
                self.generation_manager.append([self.generation, self.mdp.interaction_number, self.mdp.term_cause ])
                
                
                # Update values for the information parser (parsed to the pygame instance)
                self.information_parser['gen'] = self.generation
                self.information_parser['interactions'] = self.mdp.interaction_number
                self.information_parser['term'] = self.mdp.term_cause
                self.information_parser['action log'] = self.actions_logger
                if self.mdp.agent.state.key_found: self.information_parser['keys'] += 1
                
                if self.mdp.term_cause == "hole":
                    self.information_parser['fails'] += 1
                else:
                    self.information_parser['successes'] += 1
                
                # Printing generation information
                print(f'Generation information:\
                        \n Generation number: {self.generation} \
                            \n Interaction steps: {self.mdp.interaction_number}\
                                \n Termination cause: {self.mdp.term_cause}')
                
                # Log data for the terminated MDP
                self.logger.write_to_csv("episode_data", term_data)
                self.logger.write_to_csv("reward_data", reward_data)
                # self.logger.write_to_reward_csv(data)
                
                self.generation += 1
                
                self.mdp = self.mdp_copy.copy()
                self.pg.mdp = self.mdp
                
                self.reset_event.set()
            self.q_values_log = q_agent.q_values

# manager for saving/loading CSV files
generation_csv = CsvManager("episode_data", ["Generation number", "Interaction steps", "Termination cause"])
reward_csv = CsvManager("reward_data", ["Generation number","Reward", "Termination cause"])

logger = Logger(generation_csv, reward_csv)
plotter = Plotter(generation_csv, reward_csv)

# want plots or not?
plotting = True

# determines whether or not to use saved q values
get_q_values = True
# get_q_values = False

# Initialize the tracker
tracker = Tracker(mdp, stop_event, reset_event, q_agent, logger, get_q_values)

# define threads
pygame_thread = threading.Thread(target=tracker.pg.start_game_mdp, args=( stop_event, reset_event))
mdp_thread = threading.Thread(target=tracker.run_mdp, args=())

# Start both threads
if use_pg: pygame_thread.start()
mdp_thread.start()

# Wait for both threads to finish (although they will run indefinitely)
if use_pg: pygame_thread.join()
mdp_thread.join()

# finishing off saving/loading
logger.close_csv_files()
logger.save_q_values_log(tracker.q_values_log)


# Plots if wanted
if plotting:
    plotter.plot_data(csv_manager=generation_csv)
    plotter.plot_data(reward_csv)

    plt.show()

print("--SCRIPT ENDING")