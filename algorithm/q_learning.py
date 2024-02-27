import random
import numpy as np


class QLearningAgent:
    def __init__(self, state_space_size, action_space_size, learning_rate, discount_factor, exploration_rate):
        self.q_values = {}
        self.state_space_size = state_space_size
        self.action_space_size = action_space_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate

    def get_q_value(self, state, action):
        # Retrieve Q-value from the Q-table
        return self.q_values.get((state, action), 0.0)

    def update_q_value(self, state, action, new_value):
        # Update Q-value in the Q-table
        self.q_values[(state, action)] = new_value

    def choose_action(self, state):
        # Epsilon-greedy policy for action selection
        if random.uniform(0, 1) < self.exploration_rate:
            return random.choice(range(self.action_space_size))
        else:
            state_tuple = tuple(state)
            # Choose the action with the highest Q-value
            return max(range(self.action_space_size), key=lambda a: self.get_q_value(state, a))
