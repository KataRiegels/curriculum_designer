from __future__ import annotations

print("--SCRIPT STARTING")
import sys
import os
path = os.path.abspath("domains"); sys.path.append(path)
path = os.path.abspath("algorithm"); sys.path.append(path)
import threading
from algorithm import *
# from algorithm import QLearningAgent,QAgent,  Policy, SarsaAgent, SuccessTracker
from domains import *
from helpers import *
import time
import csv
import statistics as st
import numpy as np
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
feature_vector = Features(GridSize(10,10), Hole(exists = True))
# old_mdp = MDP(features = feature_vector, run_with_print=True, terminations = [termination_pit])
old_mdp = MDP(features = feature_vector, run_with_print=True)
mdp = old_mdp
# mdp = task_simplification(MDP(features = feature_vector, run_with_print=True))

#17 sensors with a feature range of 0-20 or 0-1 if boolean
state_space_ranges = np.array([[0, 20], [0, 20], [0, 20], [0, 20], [0, 20], [0, 20], [0, 20], [0, 20], [0, 20], [0, 20], [0, 20], [0, 20], [0, 20], [0, 20], [0, 20], [0, 20], [0, 1]])
tile_coder = tile_code.TileCoder(10, 4, state_space_ranges)

learning_alg = "QLearning"
learning_alg = "Sarsa"

if learning_alg == "QLearning":
    q_agent = QLearningAgent(10000, 5000000, (mdp.grid.height * mdp.grid.width), 4, 0.1, 0.9, 0.1)
if learning_alg == "Sarsa":
    # q_agent = SarsaAgent(10000, 500000, (mdp.grid.height * mdp.grid.width), 4, 0.1, 0.9, 0.2)
    q_agent = SarsaAgent(max_training_episodes=10000, max_steps= 500000, state_space_size=(mdp.grid.height * mdp.grid.width), action_space_size=4, learning_rate=0.1, discount_factor=0.9, exploration_rate=0.1)
    # q_agent = SarsaAgent(10000, 500000, (mdp.grid.height * mdp.grid.width), 4, 0.1, 0.9, 0.0)


use_pg = False
use_pg = True



class Tracker():
    
    
    def __init__(self, mdp : MDP, events : Events, q_agent : QAgent, logger, load_q = False, learning_alg = "QLearning"):
        # Assign parameters as attributes
        self.events = events
        self.q_agent = q_agent;       self.logger = logger;           self.learning_alg = learning_alg
        self.q_agent_copy  =  self.q_agent.copy()
        self.q_agent_target = self.q_agent.copy(); self.q_agent_target_copy = self.q_agent_target.copy()
        self.task_numbering = 0; self.current_parent_mdp = 0
        
        # Initialize attributes with default
        self.generation_manager = []; self.generation = 0; self.reward_logger = []
        self.information_parser = {}; self.q_values_log = []; self.samples = X()
        self.q_value_log_trigger = False
        
        self.mdp = mdp; self.mdp_copy = self.mdp.copy(); 
        self.mdp_target = self.mdp.copy(); self.mdp_target.target_task = True
        self.mdp_target_clean = self.mdp_target.copy()
        q_values_dummy = {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0}
        self.grid_matrix = [[q_values_dummy for _ in range(self.mdp.grid.width)] for _ in range(self.mdp.grid.height)]
        
        # Pygame instantiating
        self.pg = PygameInstance()
        self.pg.mdp = self.mdp
        
        self.success_tracker = SuccessTracker(success_threshhold=2)

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
        self.information_parser["sarsa"] = [0,0]
    
    
    def generate_curriculum(self, target_mdp : MDP, policy, beta, delta, epsilon):
        target_mdp.target_task = True
        target_mdp.task_type = "Target"
        target_mdp.mdp_num = self.task_numbering
        self.task_numbering += 1
        print(f'TARGET MDP: {target_mdp}')
        curriculum : list[MDP]= []
        while not self.events["stop"].is_set(): 
            size = len(curriculum)
            print(f'generate curriculum loop')
            
            (new_policy, curriculum) = self.recurse_task_select(target_mdp.copy(), policy, beta, epsilon, curriculum)
            print(f'(policy, curriculum) = {len(new_policy) if new_policy else new_policy }, {curriculum}')
            
            if new_policy == None:
                # print(f'main new policy length {len(new_policy)}')
                beta *= 1.2 # fix
                del curriculum[-size:]
                continue
            target_mdp.target_task = True
            policy = new_policy
            if self.evaluate(target_mdp, policy) > delta:
                print(f'Curriculum done! {curriculum} \n  ')
                # self.events["stop"].set()
                break
        return (policy, curriculum)
        
    def evaluate(self, target_mdp : MDP, policy : Policy) -> float:
        accu_reward = self.simulate_episode(target_mdp, policy)
        print(f'accumulated reward: {accu_reward}')
        return accu_reward
        pass
    
    def recurse_task_select(self, mdp : MDP, policy, beta, epsilon, curriculum):
        print(f'----- RECURSETASKSELECT WITH {mdp} ----------------- ')
        self.current_parent_mdp = mdp.mdp_num
        # mdp = mdp.copy()
        if self.events["stop"].is_set(): 
            return (None, curriculum)
        # 1        
        # solved, x, new_policy = self.learn(self.q_agent_target_copy.copy(), mdp, policy, beta)
        solved, x, new_policy = self.learn(self.q_agent, mdp, policy, beta)
        # 2 - 5
        if solved: 
            print(f'solved with ({len(new_policy)}, {curriculum})')
            self.enqueue(curriculum, mdp)
            return (new_policy, curriculum)
        # 6
        source_tasks = self.create_source_tasks(mdp, x, self.q_agent.learned_values)
        # 7 - 8
        p = []; u = []
        # 9 - 16
        for Ms in source_tasks:
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
            (best_policy, best_mdp, score) = self.get_best_policy(p, policy, x)
            print(f'best score: {score}')
            if score > epsilon:
                self.enqueue(curriculum, best_mdp)
                return (best_policy, curriculum)
        # 24
        self.sort_by_sample_relevance(u, x, epsilon)
        
        print(f'u: {len(u)}, p: {len(p)}')
        if len(p)<1 and not mdp.target_task:
            return (None, curriculum)
        # 25 - 30
        for (Ms, X_Ms) in u:
            (new_policy, curriculum) = self.recurse_task_select(Ms, policy, beta, epsilon, curriculum)
            if new_policy != None:
                print(f'running RTS with new policy: {len(new_policy)}')
                return  self.recurse_task_select(mdp, new_policy, beta, epsilon, curriculum)
        # 31
        return (None, curriculum)

    def sort_by_sample_relevance(self, u: list[tuple[MDP, X]], x: X, epsilon: int):
        
        def compute_score(X_ms: X, x: X) -> float:
            try:
                compared_count = X_ms.count_same_states(x)
            except:
                print("exception???")
            if len(x) > 0:
                ratio = compared_count / len(x)
                if compared_count / len(x) < epsilon:
                    return 0
                return ratio
            else:
                return 0
        # Filter out elements that don't meet the epsilon requirement
        u_filtered = [(mdp, X_ms) for mdp, X_ms in u if compute_score(X_ms, x) > 0]
        
        # Sort the filtered list by relevance score
        u = sorted(u_filtered, key=lambda pair: compute_score(pair[1], x))
        
        return u
        
    def get_best_policy(self, p : list[tuple[Policy, MDP]], policy : Policy, x : X) -> tuple[Policy, MDP, float]:
        best_policy = None
        best_mdp = None
        best_score = 0

        print(f'policy: {len(policy)}')

        for policy_task_pair in p:
            # if len(policy) == 0:
            #     return best_policy, best_mdp, best_score
            policy_Ms, Ms = policy_task_pair
            print(f'policy_Ms: {len(policy_Ms)}')
            compared_count = 0
            # print(f'x: {x}')
            for sample in x:
                state, action, new_state, reward = sample.get_attributes()
                if state in policy: 
                    # print(f'in policy: {state}', end = "")
                    if state in policy_Ms:
                        # print(f'')
                        # print(f'in MS: {state}')
                        # print(f'state exist: {state}', end = "")
                    
                        if policy[state] != policy_Ms[state]:
                            compared_count += 1
                # else:
                #     print(f'state doesnt exist: {state}', end = " ")
            score = compared_count / len(x)
            
            # Update best policy-task pair if the score is better
            if score >= best_score:
                best_score = score
                best_policy = policy_Ms
                best_mdp = Ms
        print(f'best policy mdp: {best_mdp}')
        return best_policy, best_mdp, best_score


    
    def create_source_tasks(self, mdp : MDP, x, v = None) -> list[MDP]:
        """Creates a set of source tasks"""
        source_task_set = []
        # How many source tasks to create?
        for _ in range(3):
            source_task = self.create_source_task(mdp, x, v)
            source_task.mdp_num = f'({self.current_parent_mdp}, {self.task_numbering})'
            source_task_set.append(source_task)
            self.task_numbering += 1

        print(f' ')
        return source_task_set

    def create_source_task(self, mdp, x, v = None):
        source_task_generators = [task_simplification, option_sub_goals]
        # source_task_generators = [task_simplification]
        # source_task_generators = [option_sub_goals]
        generator_choice = random.choice(source_task_generators)
        print(f'source task type: {generator_choice.__name__}', end = " ")
        threshold = 200
        source_mdp = generator_choice(mdp, X = x, V = v , threshold = threshold)
        
        source_mdp.target_task = False
        return source_mdp
    
    def run_mdp(self):
        """ Threading function -  runs learn"""
        # Run the learning agent
        
        states = self.mdp_target.visit_all_states()
        
        init_policy = Policy()
        init_policy.init_policy_from_states(states)
        
        run_num = 3
        
        curriculum_generations = []
        for i in range(run_num):
            self.generate_curriculum(target_mdp=self.mdp_target,policy = init_policy, beta= 10000, delta= 600, epsilon=0.1)
            print(f'Curriculum generations: {self.generation}')
            curriculum_generations.append(self.generation)
            self.generation = 0
            
        print(f'avg curriculum: {st.mean(curriculum_generations)}')

        non_curr_generations = []
        for i in range(run_num):
            while True:
                solved, x, policy = self.learn(self.q_agent_copy.copy(), self.mdp_target.copy(), beta = 500000000)
                if solved or self.events["stop"].is_set(): break
            non_curr_generations.append(self.generation)
            print(f'gen donee')
            self.generation = 0
        print(f'avg basic: {st.mean(non_curr_generations)}')
            
        
        # self.learn(self.q_agent_target, self.mdp_target.copy())
        
        # # Save values
        # self.save_q_values()
        
        # while not self.events["stop"].is_set():
        #     if self.events["mdp_type"].value == "source":
        #         source_mdp = self.create_source_task(self.mdp, self.q_agent_target.x)
        #         print(f'Next MDP? Grid size is: {source_mdp.grid.size}')
        #         self.learn(self.q_agent_copy.copy(), source_mdp)
        #     elif self.events["mdp_type"].value == "optimal":
        #         self.run_with_policy()
        self.events["stop"].set()
    
    def learn(self, q_agent : QAgent, mdp = None, policy = None, beta = 50000000):
        self.accu_reward = 0; self.mdp = mdp; 
        self.mdp_copy = mdp.copy(); 
        self.pg.mdp = self.mdp
        q_agent.x = X()
        q_agent.q_values = {}
        time_steps = 0
        if not policy == None:
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

            encoded_current_sensors = tile_coder.encode(current_state)
            # print(f"CURRENT STATE: {current_state}")
            # print(f"ENCODED CURRENT STATE: {encoded_current_sensors}")
            # print(f"CURRENT SENSORS: {current_sensors}")
            # print(" ")
            #print(f"ENCODED CURRENT SENSORS: {encoded_current_state}")
            current_action_space = self.mdp.get_action_space(current_state)
            # Decide the action to take
            action = q_agent.choose_action(encoded_current_sensors, current_action_space)
            
            
            new_state, reward, done = self.mdp.take_action(action)
            new_sensors = new_state.sensors
            encoded_new_sensors = tile_coder.encode(new_state)
            self.accu_reward += reward
            
            new_action_space = self.mdp.get_action_space(new_state)
            # print(f'--- current action space: {current_action_space}')
            # print(f'action : {action}')
            # print(f'position : {new_state.coordinate}')
            # print(f'new action space: {new_action_space}')
            # specify new state/sensors
            if not q_agent.use_optimal:
                next_action = self.q_agent.choose_policy_action(encoded_new_sensors, new_action_space)
                # print(f'next action: {next_action}')
                self.information_parser["sarsa"] = next_action
                q_agent.calculate_and_update_q_value(encoded_current_sensors, action, encoded_new_sensors, next_action, reward, current_action_space)
                    
            #This might need to be changed to "current_sensor" instead of "current_state"
            # solved = self.success_tracker.update_path(current_state)
            self.success_tracker.update_path(current_state)
            
            # Add the trajectory examples
            q_agent.x.add_sample(encoded_current_sensors, action, encoded_new_sensors, reward)

            x = q_agent.x
            
            q_values = [q_agent.get_q_value(encoded_new_sensors, a) for a in range(4)]
            self.information_parser['q_values'] = q_values

            self.grid_matrix[new_state.x][new_state.y] = q_agent.get_q_values_for_state(encoded_new_sensors)
            self.information_parser["q_values_grid"] = self.grid_matrix
            
            # if self.mdp.mdp_ended == True:
            time_steps += 1
            if done == True:
                solved = self.reset_mdp(reward)
                if solved:
                    break
        # if not beta > time_steps:
        #     print(f'Beta exceeded')
        policy = q_agent.policy.copy()
        # if self.mdp.mdp_ended == True:
        self.reset_mdp(0)
        return (solved, x, policy )
        
    def simulate_episode(self, mdp : MDP = None, policy = None, beta = 5000):
        self.accu_reward = 0; self.mdp = mdp.reset_mdp(); self.mdp_copy = mdp.copy(); self.pg.mdp = self.mdp
        q_agent = self.q_agent_copy.copy()
        q_agent.x = X()
        time_steps = 0
        if policy != None:
            q_agent.set_q_values_from_policy(policy)
        solved = False
        x = X()
        # time.sleep(2)
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
            
            encoded_current_sensors = tile_coder.encode(current_state)
            
            current_action_space = self.mdp.get_action_space(current_state)
            # Decide the action to take
            action = q_agent.choose_policy_action(encoded_current_sensors, current_action_space)
            
            
            new_state, reward, done = self.mdp.take_action(action)
            new_sensors = new_state.sensors
            encoded_new_sensors = tile_coder.encode(new_state)
            
            self.accu_reward += reward
            
            #This might need to be changed to "current_sensor" instead of "current_state"
            self.success_tracker.update_path(current_state)
            
            # Add the trajectory examples
            q_agent.x.add_sample(encoded_current_sensors, action, encoded_new_sensors, reward)

            x = q_agent.x
            
            q_values = [q_agent.get_q_value(encoded_new_sensors, a) for a in range(4)]
            self.information_parser['q_values'] = q_values
            # if new_state.key_found :
            #     print(f'found the key.\nq value:  {max(q_values)}\
            #             \nposition:  {current_state.position}')

            self.grid_matrix[new_state.x][new_state.y] = q_agent.get_q_values_for_state(encoded_new_sensors)
            # self.grid_matrix[current_state.x][current_state.y] = q_agent.get_q_values_for_state(current_state.sensors)
            self.information_parser["q_values_grid"] = self.grid_matrix
            
            # if self.mdp.mdp_ended == True:
            time_steps += 1

            if done == True:
                break
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
        # self.mdp = self.mdp_copy.copy()
        self.mdp = self.mdp.reset_mdp()
        self.pg.mdp = self.mdp
        # print(f'reset mdp here with state {self.mdp.agent.state}')
        
        self.events["reset"].set()
        return success
        
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
                self.success_tracker.start_new_path()
            else:
                # print(f'Same route taken {self.success_tracker.success_threshhold} amount of times! optimal policy found')
                return True
        else:
            self.success_tracker.path_count = 0
            self.success_tracker.start_new_path()

        self.success_tracker.save_path(current_path)
        return False
    def enqueue(self, curriculum, mdp):
        curriculum.append(mdp)
    

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



