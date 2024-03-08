import sys
import os
path = os.path.abspath("domains")
# path = os.path.abspath("algorithm")
sys.path.append(path)
path = os.path.abspath("algorithm")
sys.path.append(path)
# from ..domains.M import *
print("--SCRIPT STARTING")
from algorithm.q_learning import *
from algorithm.policy import *
from algorithm.sarsa import *
from algorithm.success_tracker import *
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
go_to_optimal_event = threading.Event()

# creates target task and simplified version
feature_vector = Features(GridSize(), Hole(exists = True))
old_mdp = MDP(features = feature_vector, run_with_print=True)
mdp = old_mdp
# mdp = task_simplification(MDP(features = feature_vector, run_with_print=True))

learning_alg = "QLearning"
learning_alg = "Sarsa"

if learning_alg == "QLearning":
    q_agent = QLearningAgent(10000, 5000000, (mdp.grid.height * mdp.grid.width), 4, 0.1, 0.9, 0.2)
if learning_alg == "Sarsa":
    # q_agent = SarsaAgent(10000, 500000, (mdp.grid.height * mdp.grid.width), 4, 0.1, 0.9, 0.2)
    q_agent = SarsaAgent(10000, 500000, (mdp.grid.height * mdp.grid.width), 4, 0.1, 0.9, 0.2)
    q_agent = SarsaAgent(10000, 500000, (mdp.grid.height * mdp.grid.width), 4, 0.1, 0.9, 0.0)

use_pg = True


class Tracker():
    
    
    def __init__(self, mdp : MDP, stop_event, reset_event, go_to_optimal_event, q_agent : SarsaAgent, logger, load_q = False, learning_alg = "QLearning"):
        self.q_agent = q_agent
        self.mdp = mdp
        self.mdp_copy = self.mdp.copy()
        
        q_values_dummy = {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0}
        self.grid_matrix = [[q_values_dummy for _ in range(self.mdp.grid.width)] for _ in range(self.mdp.grid.height)]
        
        self.logger = logger
        self.learning_alg = learning_alg
        self.stop_event = stop_event
        self.reset_event = reset_event
        self.go_to_optimal_event = go_to_optimal_event
        self.pg = PygameInstance()
        self.pg.mdp = self.mdp
        self.generation_manager = []
        self.generation = 0
        self.reward_logger = []
        
        self.information_parser = {}
        self.information_parser["q_values_grid"] = self.grid_matrix
        
        self.pg.information_parser = self.information_parser
        self.information_parser["fails"] = 0
        self.information_parser["successes"] = 0
        self.information_parser["keys"] = 0
        self.information_parser['q_values'] = [0,0,0,0]
        
        self.actions_logger = {
            "up" : 0,
            "right" : 0,
            "down" : 0,
            "left" : 0,
        }
        self.information_parser["action log"] = self.actions_logger
        
        self.q_values_log = []

        self.success_tracker = SuccessTracker(success_threshhold=5)
        self.information_parser["q_agent"] = q_agent

        if load_q:
            q_values = self.logger.load_q_values_log()
            self.q_agent.q_values = q_values
            
        self.q_agent.use_optimal = False
        
        
        self.optimal_policy = self.logger.load_q_values_optimal()
        self.optimized_agent = q_agent.copy() 
        self.optimized_agent.use_optimal = True
        self.optimized_agent.set_q_values_from_policy(self.optimal_policy)
        
        self.visited_sensor = None
        
    
    def run_mdp(self):
        
        
        self.learn(self.q_agent)
        self.q_values_log = self.q_agent.q_values
        self.optimal_policy = self.q_agent.get_optimal_policy()
        print(f'Optimal policy: {self.optimal_policy}')
        
        
        self.logger.save_q_values_log("q_values_log.npy", self.q_values_log)
        self.logger.save_optimal_q_values("q_values_optimal.npy", self.optimal_policy)
        
        
        self.optimal_policy = self.logger.load_q_values_optimal()
        
        self.optimized_agent = q_agent.copy() 
        self.optimized_agent.use_optimal = True
        self.optimized_agent.set_q_values_from_policy(self.optimal_policy)
        self.learn(self.optimized_agent)
        pass
    
    def while_condition(self, q_agent):
        if q_agent.use_optimal:
            while_condition = not self.stop_event.is_set()
        else:     
            while_condition = not self.stop_event.is_set() and not self.go_to_optimal_event.is_set()
        return while_condition
    
    # def learn(self):
    def learn(self, q_agent : SarsaAgent):
        self.accu_reward = 0
        self.mdp = self.mdp_copy.copy()
        self.pg.mdp = self.mdp
        
        # while not self.stop_event.is_set():
        while self.while_condition(q_agent):
            self.information_parser["q_agent"] = q_agent
            # time.sleep(.1)
            if q_agent.use_optimal:
                time.sleep(.5)
            # else: time.sleep (0.5)
            
            # Current state before moving
            current_state = self.mdp.agent.state.copy()
            current_sensors = current_state.sensors
            
            # Decide the action to take
            
            action = q_agent.choose_action(current_sensors)
            
            new_state, reward, done = self.mdp.take_action(action)
            new_sensors = new_state.sensors
            self.accu_reward += reward
            
            """
            reward = self.mdp.R(current_state, action)
            
            # Update the agent's state
            self.mdp.agent.state = self.mdp.P(self.mdp.agent.state, action)[0][0]
            self.mdp.update_state()
            """
            
            # specify new state/sensors
            

            if not q_agent.use_optimal:
                #For Q-learning - Implement if Q-learning is used
                if learning_alg == "QLearning":
                    q_agent.calculate_and_update_q_value(current_sensors, action, new_sensors, reward)
                
                #For SARSA - Implement if SARSA is used
                if learning_alg == "Sarsa":
                    next_action = self.q_agent.choose_action(new_sensors)
                    q_agent.calculate_and_update_q_value(current_sensors, action, new_sensors, next_action, reward)
                    # current_state = new_state
                    # action = next_action
            #This might need to be changed to "current_sensor" instead of "current_state"
            self.success_tracker.update_path(current_state)

            q_values = [q_agent.get_q_value(current_sensors, a) for a in range(4)]
            self.information_parser['q_values'] = q_values

            self.grid_matrix[new_state.x][new_state.y] = q_agent.get_q_values_for_state(new_state.sensors)
            # self.grid_matrix[current_state.x][current_state.y] = q_agent.get_q_values_for_state(current_state.sensors)
            self.visited_sensor = new_sensors
            self.information_parser["q_values_grid"] = self.grid_matrix
            # print(self.information_parser["q_values_grid"])

            # If the MDP ended (aka agent reached terminal state)
            if self.mdp.mdp_ended == True:
                self.reset_mdp(reward)
                

    def reset_mdp(self, reward):
         # u pdate reward logger and data to be able to plot it later
        self.reward_logger.append(reward)
        reward_data = [self.generation, self.accu_reward, self.mdp.term_cause ]
        self.accu_reward = 0
        
        current_path = self.success_tracker.current_path
        #if self.success_tracker.track_success(current_path):
        if self.success_tracker.previous_path.copy() == current_path:
            self.success_tracker.path_count += 1
            if self.success_tracker.path_count < self.success_tracker.success_threshhold:
                print(self.success_tracker.path_count)
                print(f'Same path taken {self.success_tracker.path_count} amount of times!')
                self.success_tracker.start_new_path()
            else:
                print(f'Same route taken {self.success_tracker.success_threshhold} amount of times! optimal policy found')
                # break
        else:
            self.success_tracker.path_count = 0
            self.success_tracker.start_new_path()
            #print("New route taken! Success criteria reset")

        self.success_tracker.save_path(current_path)
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
        
        if self.mdp.term_cause == ("hole" or "holekey") :
            self.information_parser['fails'] += 1
        elif self.mdp.term_cause == "lock":
            self.information_parser['successes'] += 1
        
        # Log data for the terminated MDP
        self.logger.write_to_csv("episode_data", term_data)
        self.logger.write_to_csv("reward_data", reward_data)
        # self.logger.write_to_reward_csv(data)
        
        self.generation += 1
        
        self.mdp = self.mdp_copy.copy()
        self.pg.mdp = self.mdp
        # time.sleep(3)
            
        self.reset_event.set()
        pass
            #     #print("Restarting MDP")

            #     # update reward logger and data to be able to plot it later
            #     self.reward_logger.append(reward)
            #     reward_data = [self.generation, accu_reward, self.mdp.term_cause ]
            #     accu_reward = 0
                
            #     # update data iteration to be able to plot it later
            #     term_data = [self.generation, self.mdp.interaction_number, self.mdp.term_cause ]
                
            #     # Might be removable?
            #     self.generation_manager.append([self.generation, self.mdp.interaction_number, self.mdp.term_cause ])
                
                
            #     # Update values for the information parser (parsed to the pygame instance)
               
            #     self.information_parser['gen'] = self.generation
            #     self.information_parser['interactions'] = self.mdp.interaction_number
            #     self.information_parser['term'] = self.mdp.term_cause
            #     self.information_parser['action log'] = self.actions_logger
            #     if self.mdp.agent.state.key_found: self.information_parser['keys'] += 1
                
            #     if self.mdp.term_cause == ("hole" or "holekey") :
            #         self.information_parser['fails'] += 1
            #     elif self.mdp.term_cause == "lock":
            #         self.information_parser['successes'] += 1
                
            #     # Printing generation information
            #     # print(f'Generation information:\
            #     #         \n Generation number: {self.generation} \
            #     #             \n Interaction steps: {self.mdp.interaction_number}\
            #     #                 \n Termination cause: {self.mdp.term_cause}')
                
            #     # Log data for the terminated MDP
            #     self.logger.write_to_csv("episode_data", term_data)
            #     self.logger.write_to_csv("reward_data", reward_data)
            #     # self.logger.write_to_reward_csv(data)
                
            #     self.generation += 1
                
            #     self.mdp = self.mdp_copy.copy()
            #     self.pg.mdp = self.mdp
            #     # time.sleep(3)

            #     self.reset_event.set()
            # self.q_values_log = q_agent.q_values

# manager for saving/loading CSV files
generation_csv = CsvManager("episode_data", ["Generation number", "Interaction steps", "Termination cause"])
reward_csv = CsvManager("reward_data", ["Generation number","Reward", "Termination cause"])

logger = Logger(generation_csv, reward_csv)
plotter = Plotter(generation_csv, reward_csv)

# want plots or not?
plotting = True
plotting = False

# determines whether or not to use saved q values
get_q_values = True
get_q_values = False


# Initialize the tracker
tracker = Tracker(mdp, stop_event, reset_event, go_to_optimal_event, q_agent, logger, get_q_values, learning_alg)

# define threads
pygame_thread = threading.Thread(target=tracker.pg.start_game_mdp, args=( stop_event, reset_event, go_to_optimal_event))
mdp_thread = threading.Thread(target=tracker.run_mdp, args=())

# Start both threads
if use_pg: pygame_thread.start()
mdp_thread.start()

# Wait for both threads to finish (although they will run indefinitely)
if use_pg: pygame_thread.join()
mdp_thread.join()

# finishing off saving/loading
logger.close_csv_files()
logger.save_q_values_log("q_values_log.npy", tracker.q_values_log)
logger.save_optimal_q_values("q_values_optimal.npy", tracker.optimal_policy)


# Plots if wanted
if plotting:
    plotter.plot_data(csv_manager=generation_csv)
    plotter.plot_data(reward_csv)

    plt.show()

print("--SCRIPT ENDING")
