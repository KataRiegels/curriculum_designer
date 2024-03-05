from __future__ import annotations

# from main import Tracker
import csv
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from domains.mdp import State, Sensors


class Logger():
    def __init__(self, *csv_managers : CsvManager): 
        self.csv_managers = {}
        for csv in csv_managers:
            self.csv_managers[csv.file_name] = csv
        
        self.q_values_log_path = "q_values_log.npy"
        
        
    def write_to_csv(self, file_name, data):
        csv = self.csv_managers[file_name]
        csv.write_to_csv(data)
            
    
    def close_csv_files(self):
        for csv in self.csv_managers.values():
            csv.csv_file.close()    
        
    def save_q_values_log(self, q_values_log):
        # Convert State objects to a hashable representation (e.g., tuple)
        q_values_log_serializable = {(state.to_np_save(), action): value for (state, action), value in q_values_log.items()}
        # print(f'q log: {q_values_log_serializable}')
        np.save(self.q_values_log_path, np.array(q_values_log_serializable))

    def load_q_values_log(self):
        loaded_data = np.load(self.q_values_log_path, allow_pickle=True).item()
        # q_values_log = {(State().convert_to_loadable(state), action): value for (state, action), value in loaded_data.items()}
        q_values_log = {(Sensors.convert_to_loadable(state), action): value for (state, action), value in loaded_data.items()}
        
        
        # q_values_log = State.from_np_load(loaded_data)
        return q_values_log

class CsvManager():
    
    def __init__(self, file_name, headings):
        self.file_name = file_name 
        self.csv_file_path = file_name + ".csv" 
        self.csv_file = open(self.csv_file_path, mode='w', newline='')
        self.csv_writer= csv.writer(self.csv_file, delimiter = ";")
        self.headings = headings
        self.csv_writer.writerow(headings)
    
    def write_to_csv(self, data):
        self.csv_writer.writerow(data)
    pass    
    
class Plotter():
    
    def __init__(self, *csv_managers : CsvManager): 
        self.csv_managers = {}
        for csv in csv_managers:
            self.csv_managers[csv.file_name] = csv

    
    def read_csv_file_reward(self):
        df = pd.read_csv(self.csv_file_path_reward, delimiter=';')
        generations = df['Reward'].tolist()
        interactions = df['Interaction steps'].tolist()
        term_causes = df['Termination cause'].tolist()
        return generations, interactions, term_causes    
        
    
    def read_csv_file_termination(self):
        df = pd.read_csv(self.csv_file_path_term, delimiter=';')
        generations = df['Generation number'].tolist()
        interactions = df['Interaction steps'].tolist()
        term_causes = df['Termination cause'].tolist()
        return generations, interactions, term_causes    

    def read_csv_file(self, csv : CsvManager):
        df = pd.read_csv(csv.csv_file_path, delimiter=';')
        columns = []
        
        for column in csv.headings:
            columns.append((column, df[column].tolist()))
        
        return columns

    def plot_data(self, csv_manager : CsvManager):
        data = self.read_csv_file(csv_manager)
            
        self.plot_single_bar_chart(data[0], data[1], data[2], csv_manager.file_name)
        pass

    def plot_single_bar_chart(self, generations, interactions, term_causes, title):
        # Color bars based on termination cause
        colors = {'lock': 'blue', 'hole': 'red', "holekey" : "yellow"}
        bar_width = 0.35
        # Replace the previous bar_positions and bars lines with these
        bar_positions = [gen for gen in generations[1]]

        fig, ax = plt.subplots()
        bars = ax.bar(bar_positions, interactions[1], width=bar_width, color=[colors[cause] for cause in term_causes[1]])

        # Create a legend
        legend_labels = [plt.Line2D([0], [0], color=colors[cause], label=cause) for cause in colors]
        ax.legend(handles=legend_labels)

        ax.set_xlabel(generations[0])
        ax.set_ylabel(interactions[0])
        ax.set_title(f'Generation vs {title} Interaction Steps')

        plt.show(block=False)  # Open the first plot window without blocking

    pass












