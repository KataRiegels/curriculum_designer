from __future__ import annotations

print("--SCRIPT STARTING")
import sys
import os
path = os.path.abspath("domains"); sys.path.append(path)
path = os.path.abspath("algorithm"); sys.path.append(path)
import threading
from algorithm import QLearningAgent,QAgent,  Policy, SarsaAgent, SuccessTracker
from domains import *
from helpers import *
import time
import csv
import pandas as pd
import random
import matplotlib.pyplot as plt
from logger import Plotter, Logger, CsvManager

# stop_event = threading.Event()
# # events["reset"] = threading.Event()
# events["reset"] = CustomEvent("learn")
# go_to_optimal_event = CustomEvent("next_mdp")
# run_sleep_time_event = CustomEvent(1)

events = Events({"stop" : CustomEvent(),
                 "reset" : CustomEvent("learn"),
                 "next_mdp" : CustomEvent(),
                 "mdp_type" : CustomEvent(),
                 "run_speed" : CustomEvent(1)
                    })
print(events)

# creates target task and simplified version
feature_vector = Features(GridSize(), Hole(exists = True))
# old_mdp = MDP(features = feature_vector, run_with_print=True, terminations = [termination_pit])
old_mdp = MDP(features = feature_vector, run_with_print=True)
mdp = old_mdp
# mdp = task_simplification(MDP(features = feature_vector, run_with_print=True))

learning_alg = "QLearning"
# learning_alg = "Sarsa"12q

if learning_alg == "QLearning":
    q_agent = QLearningAgent(10000, 5000000, (mdp.grid.height * mdp.grid.width), 4, 0.1, 0.9, 0.2)
if learning_alg == "Sarsa":
    # q_agent = SarsaAgent(10000, 500000, (mdp.grid.height * mdp.grid.width), 4, 0.1, 0.9, 0.2)
    q_agent = SarsaAgent(10000, 500000, (mdp.grid.height * mdp.grid.width), 4, 0.1, 0.9, 0.2)
    # q_agent = SarsaAgent(10000, 500000, (mdp.grid.height * mdp.grid.width), 4, 0.1, 0.9, 0.0)


use_pg = True


class Tracker():
    
    
    def __init__(self, mdp : MDP, events : Events, q_agent : SarsaAgent, logger, load_q = False, learning_alg = "QLearning"):
        # Assign parameters as attributes
        self.events = events
        self.q_agent = q_agent;       self.logger = logger;           self.learning_alg = learning_alg
        self.q_agent_copy  =  self.q_agent.copy()
        self.q_agent_target = self.q_agent.copy(); self.q_agent_target_copy = self.q_agent_target.copy()
        
        # Initialize attributes with default
        self.generation_manager = []; self.generation = 0; self.reward_logger = []
        self.information_parser = {}; self.q_values_log = []; self.samples = X()
        self.q_value_log_trigger = False
        
        self.mdp = mdp; self.mdp_copy = self.mdp.copy(); 
        self.mdp_target = self.mdp.copy(); self.mdp_target.target = True
        self.mdp_target_clean = self.mdp_target.copy()
        q_values_dummy = {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0}
        self.grid_matrix = [[q_values_dummy for _ in range(self.mdp.grid.width)] for _ in range(self.mdp.grid.height)]
        
        # Pygame instantiating
        self.pg = PygameInstance()
        self.pg.mdp = self.mdp
        
        self.success_tracker = SuccessTracker(success_threshhold=5)

        # If transfer is wanted
        try:
            if load_q:
                q_values = self.logger.load_q_values_log()
                self.q_agent.q_values = q_values
        except:
            pass

        # Information parser for the PyGame
        self.pg.information_parser = self.information_parser
        self.information_parser["fails"], self.information_parser["successes"], self.information_parser["keys"] = 0, 0, 0
        self.information_parser['q_values'] = [0,0,0,0]; self.information_parser["q_values_grid"] = self.grid_matrix
        self.information_parser["q_agent"] = q_agent
    
    def create_source_task(self):
        source_task_generators = [task_simplification, option_sub_goals]
        source_task_generators = [task_simplification]
        # source_task_generators = [option_sub_goals]
        generator_choice = random.choice(source_task_generators)
        
        # source_mdp = task_simplification(self.mdp)
        threshold = 1
        source_mdp = generator_choice(self.mdp, X = self.q_agent_target.x, V = self.q_agent_target.learned_values, threshold = threshold)
        return source_mdp
        
        pass
    
    def learn(self, q_agent : QAgent, mdp = None):
        self.accu_reward = 0
        # self.mdp = self.mdp_copy.copy()
        self.mdp = mdp
        self.mdp_copy = mdp.copy()
        self.pg.mdp = self.mdp
        # time.sleep(2)
        
        
        while not self.events["stop"].is_set():
        # while self.while_condition(q_agent):
            # Checks whether we triggered termination of current MDP
            if self.events["next_mdp"].value == "next":
                self.events["next_mdp"].clear()
                self.reset_mdp(0)
                break
            
            # sets the run speed based off keyboard input
            if self.events["run_speed"].value > 0:
                time.sleep(self.events["run_speed"].value)
            self.information_parser["q_agent"] = q_agent

            
            # Current state before moving
            current_state = self.mdp.agent.state.copy()
            current_sensors = current_state.sensors
            
            # Decide the action to take
            action = q_agent.choose_action(current_sensors)
            
            new_state, reward, done = self.mdp.take_action(action)
            new_sensors = new_state.sensors
            self.accu_reward += reward
            
            # specify new state/sensors
            if not q_agent.use_optimal:
                next_action = self.q_agent.choose_action(new_sensors)
                q_agent.calculate_and_update_q_value(current_sensors, action, new_sensors, next_action, reward)
                    
            #This might need to be changed to "current_sensor" instead of "current_state"
            self.success_tracker.update_path(current_state)
            
            # Add the trajectory examples
            q_agent.x.add_sample(current_sensors, action, new_sensors, reward)

            q_values = [q_agent.get_q_value(new_sensors, a) for a in range(4)]
            self.information_parser['q_values'] = q_values
            # if new_state.key_found :
            #     print(f'found the key.\nq value:  {max(q_values)}\
            #             \nposition:  {current_state.position}')

            self.grid_matrix[new_state.x][new_state.y] = q_agent.get_q_values_for_state(new_state.sensors)
            # self.grid_matrix[current_state.x][current_state.y] = q_agent.get_q_values_for_state(current_state.sensors)
            self.information_parser["q_values_grid"] = self.grid_matrix
            
            # if done == True:
            if self.mdp.mdp_ended == True:
                self.reset_mdp(reward)
                

    
    def run_mdp(self):
        """ Threading function -  runs learn"""
        # Run the learning agent
        self.learn(self.q_agent_target, self.mdp_target.copy())
        
        # Save values
        self.q_values_log = self.q_agent.q_values
        self.optimal_policy = self.q_agent.get_optimal_policy()
        self.logger.save_q_values_log("q_values_log.npy", self.q_values_log)
        if self.q_value_log_trigger:
            self.logger.save_optimal_q_values("q_values_optimal.npy", self.optimal_policy)
        
        while not self.events["stop"].is_set():
            if self.events["mdp_type"].value == "source":
                source_mdp = self.create_source_task()
                print(f'Grid size is: {source_mdp.grid.size}')
                self.learn(self.q_agent_copy.copy(), source_mdp)
            elif self.events["mdp_type"].value == "optimal":
                self.run_with_policy()
            else:
                print(f'nothing happened???')
                
        

    def run_with_policy(self):
        # Reading values
        self.optimal_policy = self.logger.load_q_values_optimal()
        
        # Create agent using best policy from before
        self.optimized_agent = self.q_agent_target.copy() 
        self.optimized_agent.use_optimal = True
        self.optimized_agent.set_q_values_from_policy(self.optimal_policy)
        
        # Run agent from policy
        self.learn(self.optimized_agent, self.mdp_target)
        self.X = self.optimized_agent.policy
        
    def reset_mdp(self, reward):
         # u pdate reward logger and data to be able to plot it later
        self.accu_reward = 0
        self.reward_logger.append(reward)
        reward_data = [self.generation, self.accu_reward, self.mdp.term_cause ]
        # Log data for the terminated MDP
        term_data = [self.generation, self.mdp.interaction_number, self.mdp.term_cause ]
        self.logger.write_to_csv("episode_data", term_data)
        self.logger.write_to_csv("reward_data", reward_data)
        
        self.track_success()
        self.update_information_parser()
        
        # self.logger.write_to_reward_csv(data)
        
        self.generation += 1
        
        self.mdp = self.mdp_copy.copy()
        self.pg.mdp = self.mdp
            
        self.events["reset"].set()
        
    def update_information_parser(self):
        # update data iteration to be able to plot it later
        
        # Might be removable?
        self.generation_manager.append([self.generation, self.mdp.interaction_number, self.mdp.term_cause ])
        
        
        # Update values for the information parser (parsed to the pygame instance)
        self.information_parser['gen'] = self.generation
        self.information_parser['interactions'] = self.mdp.interaction_number
        self.information_parser['term'] = self.mdp.term_cause
        if self.mdp.agent.state.key_found: self.information_parser['keys'] += 1
        
        if self.mdp.term_cause == ("hole" or "holekey") :
            self.information_parser['fails'] += 1
        elif self.mdp.term_cause == "lock":
            self.information_parser['successes'] += 1
            
        if ((self.information_parser["fails"]+self.information_parser["successes"]) != 0):
            fail_success = self.information_parser["successes"]/(self.information_parser["fails"]+self.information_parser["successes"])
            if fail_success > 0.7:
                self.q_value_log_trigger
                

                
    def track_success(self):
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
tracker = Tracker(mdp, events, q_agent, logger, get_q_values, learning_alg)

# define threads
pygame_thread = threading.Thread(target=tracker.pg.start_game_mdp, args=( (events),))
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



