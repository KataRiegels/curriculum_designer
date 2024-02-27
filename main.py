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

stop_event = threading.Event()

feature_vector = Features(GridSize(), Hole(exists = True))
mdp = MDP(features = feature_vector, run_with_print=True)
new_mdp = task_simplification(mdp)
key_pos = [1, 1]
chest_pos = [5, 7]
q_agent = QLearningAgent(2, 4, 0.1, 0.9, 0.1)

def run_mdp(new_mdp, stop_event):
    while not stop_event.is_set():

        # time.sleep(1)
        
        
        current_state = tuple([new_mdp.agent.state.x, new_mdp.agent.state.y])
        action = q_agent.choose_action(tuple(current_state))

        # action = new_mdp.agent.take_action()
        new_mdp.P(new_mdp.agent.state, action)

        print(new_mdp.state)
        
# start_game_mdp(new_mdp, key_pos, chest_pos)

# Create threads for Pygame loop and MDP loop
pygame_thread = threading.Thread(target=start_game_mdp, args=(new_mdp, key_pos, chest_pos, stop_event,))
mdp_thread = threading.Thread(target=run_mdp, args=(new_mdp,stop_event))

# Start both threads
pygame_thread.start()
mdp_thread.start()

# Wait for both threads to finish (although they will run indefinitely)
pygame_thread.join()
mdp_thread.join()

print("--SCRIPT ENDING")