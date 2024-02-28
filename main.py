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


stop_event = threading.Event()
reset_event = threading.Event()

feature_vector = Features(GridSize(), Hole(exists = True))
old_mdp = MDP(features = feature_vector, run_with_print=True)
mdp = task_simplification(MDP(features = feature_vector, run_with_print=True))
q_agent = QLearningAgent(10000, 5000000, (mdp.grid.height * mdp.grid.width), 4, 0.1, 0.9, 0.4)

use_pg = True



class Tracker():
    
    
    def __init__(self, mdp : MDP, stop_event, reset_event, q_agent, load_q = False):
        self.q_agent = q_agent
        self.mdp = mdp
        
        
        self.stop_event = stop_event
        self.reset_event = reset_event
        self.pg = PygameInstance()
        self.pg.mdp = self.mdp
        self.generation_manager = []
        self.generation = 0
        self.csv_file_path = "episode_data.csv"
        self.csv_file = open(self.csv_file_path, mode='w', newline='')
        self.csv_writer = csv.writer(self.csv_file, delimiter = ";")
        self.csv_writer.writerow(["Generation number", "Interaction steps", "Termination cause"])
        self.information_parser = {}
        self.pg.information_parser = self.information_parser
        self.information_parser["fails"] = 0
        self.information_parser["successes"] = 0
        self.information_parser["keys"] = 0
        
        
        self.q_values_log_path = "q_values_log.npy"
        if load_q:
            q_values = self.load_q_values_log()
            self.q_agent.q_values = q_values
            
    
    # def write_to_csv(self):
    #     for generation_data in self.generation_manager:
    #         self.csv_writer.writerow(generation_data)

    def save_q_values_log(self):
        np.save(self.q_values_log_path, np.array(self.q_values_log))

    def load_q_values_log(self):
        return np.load(self.q_values_log_path, allow_pickle=True).tolist()
            
    def write_to_csv(self, data):
            self.csv_writer.writerow(data)
            
    def read_csv_file(self):
        df = pd.read_csv(self.csv_file_path, delimiter=';')
        generations = df['Generation number'].tolist()
        interactions = df['Interaction steps'].tolist()
        term_causes = df['Termination cause'].tolist()
        return generations, interactions, term_causes
    
    def close_csv_file(self):
        self.csv_file.close()
    
    def run_mdp(self):
        
        
        self.mdp_copy = self.mdp.copy()
        
        while not self.stop_event.is_set():

            # time.sleep(.1)
            
            current_state = self.mdp.agent.state.copy()
            current_position = self.mdp.agent.state.coordinate
            action = self.q_agent.choose_action(current_position)
            new_state = self.mdp.agent.state
            
            old_q_value = self.q_agent.get_q_value(current_position, action)
            
            
            self.mdp.agent.state = self.mdp.P(self.mdp.agent.state, action)[0][0]
            self.mdp.update_state()
            
            reward = self.mdp.R(current_state, action)

            # new_q_value = old_q_value + self.q_agent.learning_rate * (reward + self.q_agent.discount_factor * max(self.q_agent.get_q_value(new_state.coordinate, a) for a in range(self.q_agent.action_space_size)) - old_q_value)
            new_q_value = old_q_value + self.q_agent.learning_rate * (reward + self.q_agent.discount_factor * max(self.q_agent.get_q_value(new_state, a) for a in range(self.q_agent.action_space_size)) - old_q_value)
            self.q_agent.update_q_value(new_state, action, new_q_value)

            if self.mdp.mdp_ended == True:
                print("Restarting MDP")
                data = [self.generation, self.mdp.interaction_number, self.mdp.term_cause ]
                self.generation_manager.append([self.generation, self.mdp.interaction_number, self.mdp.term_cause ])
                
                self.information_parser['gen'] = self.generation
                self.information_parser['interactions'] = self.mdp.interaction_number
                self.information_parser['term'] = self.mdp.term_cause
                if self.mdp.agent.state.key_found: self.information_parser['keys'] += 1
                
                if self.mdp.term_cause == "hole":
                    self.information_parser['fails'] += 1
                else:
                    self.information_parser['term'] += 1
                
                
                print(f'Generation information:\
                        \n Generation number: {self.generation} \
                            \n Interaction steps: {self.mdp.interaction_number}\
                                \n Termination cause: {self.mdp.term_cause}')
                self.write_to_csv(data)
                self.generation += 1
                self.mdp = self.mdp_copy.copy()
                self.pg.mdp = self.mdp
                self.reset_event.set()
        self.q_values_log = q_agent.q_values
        self.save_q_values_log()
                
tracker = Tracker(mdp, stop_event, reset_event, q_agent, False)
            
    # start_game_mdp(new_mdp, key_pos, chest_pos)
# Create threads for Pygame loop and MDP loop
pygame_thread = threading.Thread(target=tracker.pg.start_game_mdp, args=( stop_event, reset_event))
mdp_thread = threading.Thread(target=tracker.run_mdp, args=())

# Start both threads
if use_pg: pygame_thread.start()
mdp_thread.start()

# Wait for both threads to finish (although they will run indefinitely)
if use_pg: pygame_thread.join()
mdp_thread.join()

tracker.close_csv_file()
tracker.save_q_values_log()
plotting = False
if plotting:
    # Read CSV file and plot the data
    generations, interactions, term_causes = tracker.read_csv_file()

    # Color bars based on termination cause
    colors = {'lock': 'blue', 'hole': 'red'}
    bar_width = 0.35
    # Replace the previous bar_positions and bars lines with these
    bar_positions = [gen for gen in generations]

    fig, ax = plt.subplots()
    bars = ax.bar(bar_positions, interactions, width=bar_width, color=[colors[cause] for cause in term_causes])

    # Create a legend
    legend_labels = [plt.Line2D([0], [0], color=colors[cause], label=cause) for cause in colors]
    ax.legend(handles=legend_labels)

    ax.set_xlabel('Generation number')
    ax.set_ylabel('Interaction steps')
    ax.set_title('Generation vs Interaction Steps')

    plt.show()



print("--SCRIPT ENDING")