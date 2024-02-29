import random
import numpy as np


class QLearningAgent:
    def __init__(self, max_training_episodes, max_steps, state_space_size, action_space_size, learning_rate, discount_factor, exploration_rate, previous_q_values = None):
        if previous_q_values == None:
            self.q_values = {}
        else: 
            self.q_values = previous_q_values
        self.max_training_episodes = max_training_episodes
        self.max_steps = max_steps
        self.state_space_size = state_space_size
        self.action_space_size = action_space_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate

    # def get_q_value(self, state, action):
    #     # Retrieve Q-value from the Q-table
    #     #print(self.q_values)
    #     return self.q_values.get((state, action), 0.0)

    def get_q_value(self, state, action):
    # Retrieve Q-value from the Q-table
        key = (state, action)
        q_value = self.q_values.get(key, None)
        
        # if q_value is None:
        #     pass
        #     print(f"Q-value not found for key: {key}. Using default value: 0.0")
        # else: 
        #     print(f"Q-value found for key: {key} with value {q_value}")


        return q_value if q_value is not None else 0.0

    def update_q_value(self, state, action, new_value):
        # Update Q-value in the Q-table
        self.q_values[(state, action)] = new_value

    def choose_action(self, state):
        # Epsilon-greedy policy for action selection
        if random.uniform(0, 1) < self.exploration_rate:
            action = random.choice(range(self.action_space_size))
            return action
            
        else:
            # state_tuple = tuple(state)
            # Choose the action with the highest Q-value
            q_values = [self.get_q_value(state, a) for a in range(self.action_space_size)]
            
            max_q_value = max(q_values)
            max_q_indices = [i for i, q in enumerate(q_values) if q == max_q_value]

            # Randomly choose one of the actions with the maximum Q-value
            chosen_action = random.choice(max_q_indices)

            self.exploration_rate -= 0.0000001
            return chosen_action
        #print(self.exploration_rate)
