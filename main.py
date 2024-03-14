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

events = Events({"stop" : CustomEvent(),
                 "reset" : CustomEvent("learn"),
                 "next_mdp" : CustomEvent(),
                 "mdp_type" : CustomEvent(),
                 "run_speed" : CustomEvent(0)
                    })

# creates target task and simplified version
feature_vector = Features(GridSize(), Hole(exists = True))
# old_mdp = MDP(features = feature_vector, run_with_print=True, terminations = [termination_pit])
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
    # q_agent = SarsaAgent(10000, 500000, (mdp.grid.height * mdp.grid.width), 4, 0.1, 0.9, 0.0)


use_pg = True


class Tracker():
    
    
    def __init__(self, mdp : MDP, events : Events, q_agent : QAgent, logger, load_q = False, learning_alg = "QLearning"):
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
    
    
    def generate_curriculum(self, target_mdp, policy, beta, delta, epsilon):
        curriculum : list[MDP]= []
        while not self.events["stop"].is_set(): 
            size = len(curriculum)
            (new_policy, curriculum) = self.recurse_task_select(target_mdp, policy, beta, epsilon, curriculum)
            if new_policy == None:
                beta *= 1.2 # fix
                print(f'line 96')
                del curriculum[-size:]
                continue
            policy = new_policy
            if self.evaluate(target_mdp, policy) > delta:
                print(f'line 99')
                break
        return (policy, curriculum)

        
    def evaluate(self, target_mdp : MDP, policy : Policy) -> float:
        accu_reward = self.simulate_episode(target_mdp, policy)
        return accu_reward
        pass
    
    def recurse_task_select(self, mdp, policy, beta, epsilon, curriculum):
        print(f'curriculum pre: {curriculum}')
        if self.events["stop"].is_set(): 
            print(f'stopped?')
            return (None, curriculum)
        # 1        
        solved, x, new_policy = self.learn(self.q_agent, mdp, policy, beta)
        # 2 - 5
        if solved: 
            print(f'solved?')
            self.enqueue(curriculum, mdp)
            return (new_policy, curriculum)
        # 6
        source_tasks = self.create_source_tasks(mdp, x)
        # 7 - 8
        p = []; u = []
        # 9 - 16
        for Ms in source_tasks:
            print(f'1')
            if Ms == None:
                print(f'No more source tasks to me generated???')
                return (None, curriculum)
            solved_Ms, X_Ms, policy_Ms = self.learn(self.q_agent, Ms, policy, beta)
            if solved_Ms:
                p.append((policy_Ms, Ms))
            else:
                u.append((Ms, X_Ms))
        # 17 -23
        if len(p) > 0:
            print(f'2')
            (best_policy, best_mdp, score) = self.get_best_policy(p, policy, x)
            if score > epsilon:
                self.enqueue(curriculum, best_mdp)
                return (best_policy, curriculum)
        # 24
        print(f'gonna sort now')
        self.sort_by_sample_relevance(u, x, epsilon)
        # 25 - 30
        for (Ms, X_Ms) in u:
            print(f'3')
            (new_policy, curriculum) = self.recurse_task_select(Ms, policy, beta, epsilon, curriculum)
            if new_policy != None:
                return  self.recurse_task_select(mdp, policy, beta, epsilon, curriculum)
        # 31
        print(f'curriculum: {curriculum}')
        return (None, curriculum)

    def sort_by_sample_relevance(self, u : list[tuple[MDP, X]], x : X, epsilon : int):
        
        def compute_score(X_ms: X, x: X) -> float:
            print(f'about to compare')
            try:
                compared_count = X_ms.count_same_states(x)
            except:
                print("exception???")
            print(f'compared {compared_count}')
            if len(x)>0:
                returner = compared_count / len(x) 
                print(f'returner was {returner}')
                return returner
            else:
                print(f'returning 0')
                return 0
            
        # sorted_u = sorted(u, key=lambda pair: compute_score(pair[1], x))
        u = sorted(u, key=lambda pair: compute_score(pair[1], x))
        return u

        
        
    def get_best_policy(self, p : list[tuple[Policy, MDP]], policy : Policy, x : X) -> tuple[Policy, MDP, float]:
        best_policy = None
        best_mdp = None
        best_score = None

        for policy_task_pair in p:
            policy_Ms, Ms = policy_task_pair
            compared_count = 0
            for sample in x:
                state, action, new_state, reward = sample.get_attributes()
                if policy[state] != policy_Ms[state]:
                    compared_count += 1
            score = compared_count / len(x)
            
            # Update best policy-task pair if the score is better
            if score > best_score:
                best_score = score
                best_policy = policy_Ms
                best_mdp = Ms

        return best_policy, best_mdp, best_score
        
        for policy_task_pair in p:
            policy_Ms = policy_task_pair[0]
            Ms = policy_task_pair[1]
            compared_count = 0
            for sample in X:
                state, action, new_state, reward = sample.get_attributes()
                if policy[state] != policy_Ms[state]:
                    compared_count += 1
            score = compared_count/len(x)
        """
        for each state in X:
            compare action from policy(s) from policy before learning Ms
                    to policy_Ms(s) from policy after learning on Ms 
        count = count number of states where action changed
        score = normalize(count) by number of states in X
            
        
        """
        
        return best_policy, best_mdp, score

    def create_source_tasks(self, mdp : MDP, x) -> list[MDP]:
        """Creates a set of source tasks"""
        source_task_set = []
        # How many source tasks to create?
        for _ in range(3):
            source_task = self.create_source_task(mdp, x)
            source_task_set.append(source_task)
        # for mdp in source_task_set:
        #     print("printing those mDPS")
        #     print(mdp)
        print(f'source MDPs: {source_task_set}')
        return source_task_set

    def enqueue(self, curriculum, mdp):
        curriculum.append(mdp)
        pass

    
    def create_source_task(self, mdp, x):
        source_task_generators = [task_simplification, option_sub_goals]
        source_task_generators = [task_simplification]
        # source_task_generators = [option_sub_goals]
        generator_choice = random.choice(source_task_generators)
        
        # source_mdp = task_simplification(self.mdp)
        threshold = 1
        source_mdp = generator_choice(mdp, X = x, V = self.q_agent_target.learned_values, threshold = threshold)
        return source_mdp
    
    
    
    def run_mdp(self):
        """ Threading function -  runs learn"""
        # Run the learning agent
        
        # self.generate_curriculum(self.mdp_target, Policy(), 50000, 1100, 5)
        
        self.learn(self.q_agent_target, self.mdp_target.copy())
        
        # Save values
        self.save_q_values()
        
        while not self.events["stop"].is_set():
            if self.events["mdp_type"].value == "source":
                source_mdp = self.create_source_task(self.mdp, self.q_agent_target.x)
                print(f'Next MDP? Grid size is: {source_mdp.grid.size}')
                self.learn(self.q_agent_copy.copy(), source_mdp)
            elif self.events["mdp_type"].value == "optimal":
                self.run_with_policy()
    
    def learn(self, q_agent : QAgent, mdp = None, policy = None, beta = 500000000):
        self.accu_reward = 0; self.mdp = mdp; self.mdp_copy = mdp.copy(); self.pg.mdp = self.mdp
        time_steps = 0
        if policy != None:
            q_agent.q_values_from_policy(policy)
        solved = False
        x = X()
        while not self.events["stop"].is_set() and beta > time_steps:
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
            solved = self.success_tracker.update_path(current_state)
            
            # Add the trajectory examples
            q_agent.x.add_sample(current_sensors, action, new_sensors, reward)

            x = q_agent.x
            
            q_values = [q_agent.get_q_value(new_sensors, a) for a in range(4)]
            self.information_parser['q_values'] = q_values
            # if new_state.key_found :
            #     print(f'found the key.\nq value:  {max(q_values)}\
            #             \nposition:  {current_state.position}')

            self.grid_matrix[new_state.x][new_state.y] = q_agent.get_q_values_for_state(new_state.sensors)
            # self.grid_matrix[current_state.x][current_state.y] = q_agent.get_q_values_for_state(current_state.sensors)
            self.information_parser["q_values_grid"] = self.grid_matrix
            
            # if self.mdp.mdp_ended == True:
            time_steps += 1
            if done == True:
                self.reset_mdp(reward)
        print(f'Finisned a learn()')
        if not beta > time_steps:
            print(f'Beta exceeded')
        policy = q_agent.policy
        return (solved, x, policy )
        
    def simulate_episode(self, mdp = None, policy = None, beta = None):
        self.accu_reward = 0; self.mdp = mdp; self.mdp_copy = mdp.copy(); self.pg.mdp = self.mdp
        q_agent = self.q_agent_copy.copy()
        q_agent.q_values_from_policy(policy)
        
        while not self.events["stop"].is_set():
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
            
            #This might need to be changed to "current_sensor" instead of "current_state"
            solved = self.success_tracker.update_path(current_state)
            
            # Add the trajectory examples
            q_agent.x.add_sample(current_sensors, action, new_sensors, reward)

            x = q_agent.x
            
            q_values = [q_agent.get_q_value(new_sensors, a) for a in range(4)]
            self.information_parser['q_values'] = q_values
            # if new_state.key_found :
            #     print(f'found the key.\nq value:  {max(q_values)}\
            #             \nposition:  {current_state.position}')

            self.grid_matrix[new_state.x][new_state.y] = q_agent.get_q_values_for_state(new_state.sensors)
            # self.grid_matrix[current_state.x][current_state.y] = q_agent.get_q_values_for_state(current_state.sensors)
            self.information_parser["q_values_grid"] = self.grid_matrix
            
            # if self.mdp.mdp_ended == True:

            if done == True:
                self.reset_mdp(reward)
        
        policy = q_agent.policy
        return (self.accu_reward )
                
    def save_q_values(self):
        self.q_values_log = self.q_agent.q_values
        self.optimal_policy = self.q_agent.get_optimal_policy()
        self.logger.save_q_values_log("q_values_log.npy", self.q_values_log)
        if self.q_value_log_trigger:
            self.logger.save_optimal_q_values("q_values_optimal.npy", self.optimal_policy)

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
        
        success = self.track_success()
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
                # print(self.success_tracker.path_count)
                # print(f'Same path taken {self.success_tracker.path_count} amount of times!')
                self.success_tracker.start_new_path()
            else:
                # print(f'Same route taken {self.success_tracker.success_threshhold} amount of times! optimal policy found')
                return True
                # break
        else:
            self.success_tracker.path_count = 0
            self.success_tracker.start_new_path()
            #print("New route taken! Success criteria reset")

        self.success_tracker.save_path(current_path)
        return False

    

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
if len(tracker.q_values_log)>1 and len(tracker.optimal_policy)>1:
    logger.save_q_values_log("q_values_log.npy", tracker.q_values_log)
    logger.save_optimal_q_values("q_values_optimal.npy", tracker.optimal_policy)


# Plots if wanted
if plotting:
    plotter.plot_data(csv_manager=generation_csv)
    plotter.plot_data(reward_csv)

    plt.show()

print("--SCRIPT ENDING")



